# Copyright 2014-2016 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3
from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)


class ImportInvoiceLine(models.TransientModel):
    _name = "import.invoice.line.wizard"
    _description = "Import supplier invoice line"


    def default_get(self, field_list):
        res = super(ImportInvoiceLine, self).default_get(field_list)
        if self.env.context.get('active_id') and 'distribution_action' in field_list:
            distribution = self.env['purchase.cost.distribution'].browse(self.env.context['active_id'])
            res['distribution_action'] = distribution.name

        return res
    distribution_action = fields.Char()
    supplier = fields.Many2one(
        comodel_name="res.partner", string="Supplier", required=True,
    )
    invoice = fields.Many2one(
        comodel_name='account.move', string="Invoice", required=True)
    # invoice = fields.Many2one(
    #     comodel_name="account.move",
    #     string="Invoice",
    #     required=True,
    #     domain="[('partner_id', '=', supplier), ('move_type', '=', 'in_invoice'),"
    #     "('state', '=', 'posted')]",
    # )
    invoice_line = fields.Many2one(
        comodel_name="account.move.line",
        string="Invoice line",
        required=True,
        domain="[('move_id', '=', invoice)]",
    )
    expense_type = fields.Many2one(
        comodel_name="purchase.expense.type", string="Expense type", required=True
    )

    def action_import_invoice_line(self):

        self.ensure_one()
        dist_id = self.env.context['active_id']
        distribution = self.env['purchase.cost.distribution'].browse(dist_id)
        amount = self.invoice_line.price_subtotal
        currency_to = distribution.currency_id
        company = distribution.company_id or self.env.user.company_id
        cost_date = self.invoice.date or fields.Date.today()
        facturas = self.env['account.move'].browse(self.invoice.id)

        if distribution.tasa_cambio == 0:
            distribution._get_tasa()

        if currency_to != facturas.currency_id:
            result = amount * distribution.tasa_cambio
            expense_amount = currency_to._convert(result, currency_to, company, cost_date)

        else:
            result = amount * 1
            expense_amount = currency_to._convert(result, currency_to, company, cost_date)

        for fact in facturas:
            fact.distribution_name = distribution.name

        movee = self.env['account.move.line'].browse(self.invoice_line.id)
        for line in movee:
            line.distribution_id = self.invoice_line.name
            line.distribution_name = distribution.name

        self.env['purchase.cost.distribution.expense'].create({
            'distribution': dist_id,
            'invoice_line': self.invoice_line.id,
            'invoice_id': self.invoice_line.move_id.id,
            'ref': self.invoice_line.name,
            'expense_amount': expense_amount,
            'type': self.expense_type.id,
            'distribution_id': self.invoice_line.name,
            'distribution_name': distribution.name,
        })

    # def action_import_invoice_line(self):
    #     self.ensure_one()
    #     dist_id = self.env.context["active_id"]
    #     distribution = self.env["purchase.cost.distribution"].browse(dist_id)
    #     currency_from = self.invoice_line.currency_id
    #     amount = self.invoice_line.price_subtotal
    #     currency_to = distribution.currency_id
    #     company = distribution.company_id or self.env.user.company_id
    #     cost_date = distribution.date or fields.Date.today()
    #     expense_amount = currency_from._convert(amount, currency_to, company, cost_date)
    #
    #     facturas = self.env['account.move'].browse(self.invoice.id)
    #     for fact in facturas:
    #         fact.distribution_name = distribution.name
    #
    #     movee = self.env['account.move.line'].browse(self.invoice_line.id)
    #     for line in movee:
    #         line.distribution_id = self.invoice_line.name
    #         line.distribution_name = distribution.name
    #
    #     self.env["purchase.cost.distribution.expense"].create(
    #         {
    #             "distribution": dist_id,
    #             "invoice_line": self.invoice_line.id,
    #             "invoice_id": self.invoice_line.move_id.id,
    #             "ref": self.invoice_line.name,
    #             "expense_amount": expense_amount,
    #             "type": self.expense_type.id,
    #             'distribution_id': self.invoice_line.name,
    #             'distribution_name': distribution.name,
    #         }
    #     )
