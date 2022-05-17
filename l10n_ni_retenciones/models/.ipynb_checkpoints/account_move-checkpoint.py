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


#     def _compute_payments_widget_to_reconcile_info(self):
#         for move in self:
#             move.invoice_outstanding_credits_debits_widget = json.dumps(False)
#             move.invoice_has_outstanding = False

#             if move.state != 'posted' \
#                     or move.payment_state not in ('not_paid', 'partial') \
#                     or not move.is_invoice(include_receipts=True):
#                 continue

#             pay_term_lines = move.line_ids\
#                 .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

#             domain = [
#                 ('account_id', 'in', pay_term_lines.account_id.ids),
#                 ('move_id.state', '=', 'posted'),
#                 ('partner_id', '=', move.commercial_partner_id.id),
#                 ('reconciled', '=', False),
#                 '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
#                 '|', ('move_id.invoice_name', '=', False), ('move_id.invoice_name', '=', self.name)
#             ]

#             payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

#             if move.is_inbound():
#                 domain.append(('balance', '<', 0.0))
#                 payments_widget_vals['title'] = _('Outstanding credits')
#             else:
#                 domain.append(('balance', '>', 0.0))
#                 payments_widget_vals['title'] = _('Outstanding debits')

#             for line in self.env['account.move.line'].search(domain):

#                 if line.currency_id == move.currency_id:
#                     # Same foreign currency.
#                     amount = abs(line.amount_residual_currency)
#                 else:
#                     # Different foreign currencies.
#                     amount = move.company_currency_id._convert(
#                         abs(line.amount_residual),
#                         move.currency_id,
#                         move.company_id,
#                         line.date,
#                     )

#                 if move.currency_id.is_zero(amount):
#                     continue

#                 payments_widget_vals['content'].append({
#                     'journal_name': line.ref or line.move_id.name,
#                     'amount': amount,
#                     'currency': move.currency_id.symbol,
#                     'id': line.id,
#                     'move_id': line.move_id.id,
#                     'position': move.currency_id.position,
#                     'digits': [69, move.currency_id.decimal_places],
#                     'payment_date': fields.Date.to_string(line.date),
#                 })

#             if not payments_widget_vals['content']:
#                 continue

#             move.invoice_outstanding_credits_debits_widget = json.dumps(payments_widget_vals)
#             move.invoice_has_outstanding = True


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
                    # print("222222222")
                    tds_amount = base * element.amount / 100
                    amount -= tds_amount

            if element.amount_type == 'division':

                if element.include_base_amount:
                    tds_amount = self.amount_total * element.amount / 100
                else:
                    # print("222222222")
                    tds_amount = amount * element.amount / 100
                    amount -= tds_amount

            code = str(element.id).split("_")           

            l.append((0, 0, {
                'code': code[1],
                'tax': element.name,
                'type_tax': element.amount_type,
                'amount': element.amount,
                'tds_amount': tds_amount,
                'currency_id': self.currency_id.id
            }))

            

        self.apliqued_witholding = l

    @api.onchange('withholdings')
    @api.depends('withholdings')
    def onchange_payment_way(self):
        self.compute_witholding()


    def revert_retention(self):
        retentions = [ move.id for move in self.env['account.move'].search([('invoice_name', '=', self.name)])]
        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move", active_ids=retentions).create({
            'date': fields.Date.from_string('2021-09-09'),
            'reason': 'Asociada a la factura %s' % self.name,
            'refund_method': 'cancel',
        })
        reversal = move_reversal.reverse_moves()

        self.withholdings = False
        self.tds = False
        self.apliqued_witholding.unlink()
        
        #print("RTENCIONES ******%s" % retentions)


    def add_retention(self):

        if self.move_type == 'out_invoice':
            self.add_retention_client()
        elif self.move_type == 'in_invoice':
            self.add_retention_supplier()
        self.tds = True



    def add_retention_client(self):

        for tds in self.apliqued_witholding:

            AccountMove = self.env['account.move']
            lines_ids = []
            

            tax = self.env['account.tax'].search([('id', '=', tds.code)])
            amount_currency = self.currency_id._convert(tds.tds_amount, self.company_id.currency_id, self.company_id, self.date)

            #_logger.info("adscdvn %s" % [tax, tds, tds.tax, tds.tds_amount, tds.code])
            aux = 0.0
            for element in tax.invoice_repartition_line_ids:
                if element.repartition_type == 'tax':
                    tax_amount = amount_currency * element.factor
                    aux+= tax_amount

                    debit_line = (0, 0, {
                        'name': _('%s Asiento de retención %s ') % (
                            self.env.user.name, self.name),
                        'account_id': element.account_id.id,
                        'journal_id': tax.journal_id.id,
                        'debit': abs(tax_amount),
                        'credit': 0,
                    })

                    lines_ids.append(debit_line)

            credit_line =  (0, 0, {
                        'name': _('%s Asiento por retención %s ') % (
                            self.env.user.name, self.name),
                        'account_id': self.partner_id.property_account_receivable_id.id,
                        'partner_id': self.partner_id.id,
                        'journal_id': tax.journal_id.id,
                        'debit': 0,
                        'credit': abs(aux),
                    })

            lines_ids.append(credit_line)

            move_vals = {
                'journal_id': tax.journal_id.id,
                'company_id': self.company_id.id,
                'ref': "Retención " + tax.name,
                'partner_id': self.partner_id.id,
                'move_type': 'entry',
                'line_ids': lines_ids,
            }

            move = AccountMove.create(move_vals)
            move.invoice_name = self.name
            move.post()

    def add_retention_supplier(self):

        for tds in self.apliqued_witholding:

            AccountMove = self.env['account.move']
            lines_ids = []

            tax = self.env['account.tax'].search([('id', '=', tds.code)])
            
            
            amount_currency = self.currency_id._convert(tds.tds_amount, self.company_id.currency_id, self.company_id, self.date)
            
            aux = 0.0
            for element in tax.invoice_repartition_line_ids:
                if element.repartition_type == 'tax':
                    tax_amount = amount_currency * element.factor
                    aux += tax_amount

                    credit_line = (0, 0, {
                        'name': _('%s Asiento de retención %s ') % (
                            self.env.user.name, self.name),
                        'account_id': element.account_id.id,
                        'journal_id': tax.journal_id.id,
                        'debit': 0,
                        'credit': abs(tax_amount),
                    })

                    lines_ids.append(credit_line)

            debit_line = (0, 0, {
                'name': _('%s Asiento por retención %s ') % (
                    self.env.user.name, self.name),
                'account_id': self.partner_id.property_account_payable_id.id,
                'partner_id': self.partner_id.id,
                'journal_id': tax.journal_id.id,
                'debit': abs(aux),
                'credit': 0,
            })

            lines_ids.append(debit_line)

            move_vals = {
                'journal_id': tax.journal_id.id,
                'company_id': self.company_id.id,
                'ref': "Retención " + tax.name,
                'partner_id': self.partner_id.id,
                'move_type': 'entry',
                'line_ids': lines_ids,
            }

            move = AccountMove.create(move_vals)
            move.invoice_name = self.name
            move.post()

class payment_tds(models.Model):
    _name = "invoice.retention"
    code = fields.Char(string="Id")
    tax = fields.Char(string="Nombre")
    type_tax = fields.Char(string="Cálculo de Impuesto")
    amount = fields.Float(string='Importe')
    tds_amount = fields.Monetary(string="Monto de Retención", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
