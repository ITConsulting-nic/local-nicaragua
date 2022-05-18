# Copyright 2013 Joaquín Gutierrez
# Copyright 2014-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_open_landed_cost(self):
        self.ensure_one()
        line_obj = self.env['purchase.cost.distribution.line']
        lines = line_obj.search([('purchase_id', '=', self.id)])
        if lines:
            return lines.get_action_purchase_cost_distribution()


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    price_unit_old = fields.Float(string='Precio unitario previo', required=True,
                                  digits=dp.get_precision('Product Price'))
