# Copyright 2014-2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.move'
    distribution_name = fields.Char(default=False)

    expense_line_ids = fields.One2many(
        comodel_name="purchase.cost.distribution.expense",
        inverse_name="invoice_id", string="Landed costs",

    )

    # _columns = {
    #
    #     'expense_line_ids': fields.one2many('purchase.cost.distribution.expense', 'invoice_id', string="Landed costs"),
    #
    # }


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'
    distribution_id = fields.Char(default=False)
    distribution_name = fields.Char(default=False)

    expense_line_ids = fields.One2many(
        comodel_name="purchase.cost.distribution.expense",
        inverse_name="invoice_line", string="Landed costs")
