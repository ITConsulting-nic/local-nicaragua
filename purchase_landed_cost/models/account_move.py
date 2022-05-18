# Copyright 2014-2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = "account.move"
    distribution_name = fields.Char(default=False)
    expense_line_ids = fields.One2many(
        comodel_name="purchase.cost.distribution.expense",
        inverse_name="invoice_id",
        string="Landed costs",
    )

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.update({'distribution_name': False})
        return super(AccountInvoice, self).copy(default)

    # _columns = {
    #
    #     'expense_line_ids': fields.one2many('purchase.cost.distribution.expense', 'invoice_id', string="Landed costs"),
    #
    # }


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"
    invoice_id = fields.Many2one(comodel_name="account.move", string="Invoice")
    expense_line_ids = fields.One2many(
        comodel_name="purchase.cost.distribution.expense",
        inverse_name="invoice_line",
        string="Landed costs",
    )
    distribution_id = fields.Char(default=False, copy=False)
    distribution_name = fields.Char(default=False)
    # _columns = {
    #
    #     'expense_line_ids': fields.one2many('purchase.cost.distribution.expense', 'invoice_line', string="Landed costs"),
    #
    # }
