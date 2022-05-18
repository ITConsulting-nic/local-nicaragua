# Copyright 2013 Joaquín Gutierrez
# Copyright 2014-2016 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockPicking(models.Model):
    _inherit = "stock.picking"
    distribution_id = fields.Char(default=False)
    costed_date = fields.Datetime('Fecha de costeo')
    def action_open_landed_cost(self):
        self.ensure_one()
        line_obj = self.env["purchase.cost.distribution.line"]
        lines = line_obj.search([("picking_id", "=", self.id)])
        if lines:
            return lines.get_action_purchase_cost_distribution()
    #
    # def button_validate(self):
    #
    #     ctx = dict(self.env.context)
    #     ctx.pop('default_immediate_transfer', None)
    #     self = self.with_context(ctx)
    #
    #     # Sanity checks.
    #     pickings_without_moves = self.browse()
    #     pickings_without_quantities = self.browse()
    #     pickings_without_lots = self.browse()
    #     products_without_lots = self.env['product.product']
    #
    #     for picking in self:
    #
    #         if not picking.move_lines and not picking.move_line_ids:
    #             pickings_without_moves |= picking
    #
    #         picking.message_subscribe([self.env.user.partner_id.id])
    #         picking_type = picking.picking_type_id
    #         precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #         no_quantities_done = all(
    #             float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
    #             picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
    #
    #         no_reserved_quantities = all(
    #             float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line
    #             in picking.move_line_ids)
    #         if no_reserved_quantities and no_quantities_done:
    #             pickings_without_quantities |= picking
    #
    #         if picking_type.use_create_lots or picking_type.use_existing_lots:
    #             lines_to_check = picking.move_line_ids
    #             if not no_quantities_done:
    #                 lines_to_check = lines_to_check.filtered(
    #                     lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
    #             for line in lines_to_check:
    #                 product = line.product_id
    #                 if product and product.tracking != 'none':
    #                     if not line.lot_name and not line.lot_id:
    #                         pickings_without_lots |= picking
    #                         products_without_lots |= product
    #
    #     if not self._should_show_transfers():
    #
    #         if pickings_without_moves:
    #             raise UserError(_('Please add some items to move.'))
    #         if pickings_without_quantities:
    #             raise UserError(self._get_without_quantities_error_message())
    #         if pickings_without_lots:
    #             raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(
    #                 products_without_lots.mapped('display_name')))
    #     else:
    #         message = ""
    #         if pickings_without_moves:
    #             message += _('Transfers %s: Please add some items to move.') % ', '.join(
    #                 pickings_without_moves.mapped('name'))
    #         if pickings_without_quantities:
    #             message += _(
    #                 '\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(
    #                 pickings_without_quantities.mapped('name'))
    #         if pickings_without_lots:
    #             message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (
    #             ', '.join(pickings_without_lots.mapped('name')),
    #             ', '.join(products_without_lots.mapped('display_name')))
    #         if message:
    #             raise UserError(message.lstrip())
    #
    #     # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
    #     # moves and/or the context and never call `_action_done`.
    #
    #     if not self.env.context.get('button_validate_picking_ids'):
    #         self = self.with_context(button_validate_picking_ids=self.ids)
    #     res = self._pre_action_done_hook()
    #
    #     if res is not True:
    #
    #         return res
    #
    #     # Call `_action_done`.
    #     if self.env.context.get('picking_ids_not_to_backorder'):
    #         pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
    #         pickings_to_backorder = self - pickings_not_to_backorder
    #     else:
    #         pickings_not_to_backorder = self.env['stock.picking']
    #         pickings_to_backorder = self
    #
    #
    #     pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
    #     pickings_to_backorder.with_context(cancel_backorder=False)._action_done()
    #     return True
    #
    #
    # def _action_done(self):
    #     """Call `_action_done` on the `stock.move` of the `stock.picking` in `self`.
    #     This method makes sure every `stock.move.line` is linked to a `stock.move` by either
    #     linking them to an existing one or a newly created one.
    #
    #     If the context key `cancel_backorder` is present, backorders won't be created.
    #
    #     :return: True
    #     :rtype: bool
    #     """
    #
    #     self._check_company()
    #
    #     todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
    #     for picking in self:
    #         if picking.owner_id:
    #             picking.move_lines.write({'restrict_partner_id': picking.owner_id.id})
    #             picking.move_line_ids.write({'owner_id': picking.owner_id.id})
    #     todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
    #     self.write({'date_done': fields.Datetime.now(), 'priority': '0'})
    #
    #     # if incoming moves make other confirmed/partially_available moves available, assign them
    #     done_incoming_moves = self.filtered(lambda p: p.picking_type_id.code == 'incoming').move_lines.filtered(lambda m: m.state == 'done')
    #     done_incoming_moves._trigger_assign()
    #
    #     self._send_confirmation_email()
    #     return True