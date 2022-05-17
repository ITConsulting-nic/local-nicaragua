# -*- coding: utf-8 -*-
# Copyright (C) 2017-present  Technaureus Info Solutions(<http://www.technaureus.com/>).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from json import dumps
import json
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def external_lay_aux(self, aux):
        result = "false"
        if aux == "report_retenciones":
            campo = self.env['ir.config_parameter'].sudo().get_param('l10n_ni_retenciones.report_retenciones')
            if campo:
                result = "true"
            else:
                result = "false"
        return result

    @api.onchange('withholdings')
    def onchange_withholdings(self):
        for rec in self:
            if rec.move_type == 'out_invoice':
                return {'domain': {'withholdings': [('tds', '=', True), ('type_tax_use', '=', 'sale')], }}
            elif rec.move_type == 'in_invoice':
                return {'domain': {'withholdings': [('tds', '=', True), ('type_tax_use', '=', 'purchase')] }}

    withholdings = fields.Many2many('account.tax', string='Retenciones')
    apliqued_witholding = fields.Many2many('invoice.retention', string='Retenciones')
    tds = fields.Boolean('Retención', default=False)
    invoice_name = fields.Char(string="Nombre de factura")

    tax_type = fields.Char(compute='_compute_tax_type')


    def _compute_tax_type(self):
        self.tax_type = self.journal_id.type



    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False

            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue

            pay_term_lines = move.line_ids\
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('move_id.state', '=', 'posted'),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
                '|', ('move_id.invoice_name', '=', False), ('move_id.invoice_name', '=', self.name)
            ]

            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

            if move.is_inbound():
                domain.append(('balance', '<', 0.0))
                payments_widget_vals['title'] = _('Outstanding credits')
            else:
                domain.append(('balance', '>', 0.0))
                payments_widget_vals['title'] = _('Outstanding debits')

            for line in self.env['account.move.line'].search(domain):

                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = move.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )

                if move.currency_id.is_zero(amount):
                    continue

                payments_widget_vals['content'].append({
                    'journal_name': line.ref or line.move_id.name,
                    'amount': amount,
                    'currency': move.currency_id.symbol,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'position': move.currency_id.position,
                    'digits': [69, move.currency_id.decimal_places],
                    'payment_date': fields.Date.to_string(line.date),
                })

            if not payments_widget_vals['content']:
                continue

            move.invoice_outstanding_credits_debits_widget = json.dumps(payments_widget_vals)
            move.invoice_has_outstanding = True


    def action_register_payment(self):

        if len(self.withholdings) != 0 and not self.tds :
            raise ValidationError("No puede realizar el pago, sin aplicar las retenciones")
        else:
            return super(AccountMove, self).action_register_payment()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['withholdings'] = []
        default['apliqued_witholding'] = []
        return super(AccountMove, self).copy(default)

    def compute_witholding(self):
        l = []
        self.apliqued_witholding = False
        amount = self.amount_total
        base = self.amount_untaxed

        for element in self.withholdings:
            tds_amount = 0

            if element.amount_type == 'percent':
                if element.include_base_amount:
                    tds_amount = self.amount_untaxed * element.amount / 100
                else:
                    tds_amount = base * element.amount / 100
                    amount -= tds_amount

            if element.amount_type == 'division':

                if element.include_base_amount:
                    tds_amount = self.amount_total * element.amount / 100
                else:
                    tds_amount = amount * element.amount / 100
                    amount -= tds_amount

            code = str(element.id).split("_")           

            company_amount = self.currency_id._convert(tds_amount, self.company_id.currency_id, self.company_id, self.date)

            l.append((0, 0, {
                'code': code[1],
                'tax': element.name,
                'type_tax': element.amount_type,
                'amount': element.amount,
                'tds_amount': company_amount,
                'currency_id': self.company_id.currency_id.id
            }))

            

        self.apliqued_witholding = l

    @api.onchange('withholdings', 'invoice_line_ids')
    @api.depends('withholdings',  'invoice_line_ids')
    def onchange_payment_way(self):
        self.compute_witholding()


    def revert_retention(self):
        retentions = [ move.id for move in self.env['account.move'].search([('invoice_name', '=', self.name), 
        ('reversed_entry_id', '=', False),( 'reversal_move_id', '=', False)])]

        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move", active_ids=retentions).create({
            'date': fields.Date.today(),
            'reason': 'Asociada a la factura %s' % self.name,
            'refund_method': 'cancel',
        })
        reversal = move_reversal.reverse_moves()

        self.withholdings = False
        self.tds = False
        self.apliqued_witholding.unlink()


    def add_retention(self):

        if len(self.withholdings) != 0:
            action = self.env["ir.actions.actions"]._for_xml_id("l10n_ni_retenciones.action_wizard_retention_view")
            return action
        else:
             raise ValidationError("Esta factura no tiene retenciones asignadas")

    def get_tasa(self, datos):

        result = self.currency_id._convert(datos.amount_untaxed, datos.company_id.currency_id, datos.company_id, datos.invoice_date)

        # tasa_cambio = 0

        #
        # rate = self.env['res.currency.rate'].search([
        #     ('currency_id', '=', currencyid.id),
        #     ('name', '<=', self.date),
        #     ('company_id', '=', self.company_id.id),
        # ], order='name desc')
        #
        # if rate:
        #     if rate[0].rate > 0:
        #         tasa_cambio = 1 / rate[0].rate
        # else:
        #     tasa_cambio = 1
        return result

class payment_tds(models.Model):
    _name = "invoice.retention"
    code = fields.Char(string="Id")
    tax = fields.Char(string="Nombre")
    type_tax = fields.Char(string="Cálculo de Impuesto")
    amount = fields.Float(string='Importe')
    tds_amount = fields.Monetary(string="Monto de Retención", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
