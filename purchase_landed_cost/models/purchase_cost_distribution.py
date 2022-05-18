# Copyright 2013 Joaquín Gutierrez
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3


from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class PurchaseCostDistribution(models.Model):
    _name = "purchase.cost.distribution"
    _description = "Purchase landed costs distribution"
    _order = "name desc"

    tasa_cambio = fields.Float(string="Tasa de cambio", digits=(12, 4))

    cost_update_type = fields.Selection(
        [('direct', 'Direct Update')], string='Cost Update Type',
        default='direct', required=True)

    def _get_tasa(self):

        currencyid = self.env['res.currency'].search([('name', '=', 'USD')])
        rate = self.env['res.currency.rate'].search([
            ('currency_id', '=', currencyid.id),
            ('name', '<=', self.date),
            ('company_id', '=', self.company_id.id),
        ], order='name desc')
        if rate:
            if rate[0].rate > 0:
                self.tasa_cambio = 1 / rate[0].rate
        else:
            self.tasa_cambio = 1

    def action_picking_import_wizard(self):

        if self.tasa_cambio > 0:
            view_id = self.env.ref('purchase_landed_cost.picking_import_wizard_view').id

            return {
                'name': 'Import incoming shipment',
                'type': 'ir.actions.act_window',
                'views_type': 'form',
                'views_mode': 'form',
                'res_model': 'picking.import.wizard',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'target': 'new',
            }
        else:
            self._get_tasa()
            view_id = self.env.ref('purchase_landed_cost.picking_confirm_msg_wizard_view').id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Message',
                'res_model': 'confirm.msg',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(view_id, 'form')],
                'view_id': view_id,
            }

    def action_import_invoice_line_wizard(self):

        if self.tasa_cambio > 0:
            view_id = self.env.ref('purchase_landed_cost.import_invoice_line_wizard_view').id
            return {
                'name': 'Import supplier invoice line',
                'type': 'ir.actions.act_window',
                'views_type': 'form',
                'views_mode': 'form',
                'res_model': 'import.invoice.line.wizard',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'target': 'new',
            }
        else:
            self._get_tasa()
            view_id = self.env.ref('purchase_landed_cost.picking_confirm_msg_wizard_view2').id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Message',
                'res_model': 'confirm.msg',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(view_id, 'form')],
                'view_id': view_id,
            }

    @api.depends("total_expense", "total_purchase")
    def _compute_amount_total(self):
        for distribution in self:
            distribution.amount_total = (
                    distribution.total_purchase + distribution.total_expense
            )

    @api.depends("cost_lines", "cost_lines.total_amount")
    def _compute_total_purchase(self):
        for distribution in self:
            distribution.total_purchase = sum(
                [x.total_amount for x in distribution.cost_lines]
            )

    @api.depends("cost_lines", "cost_lines.product_price_unit")
    def _compute_total_price_unit(self):
        for distribution in self:
            distribution.total_price_unit = sum(
                [x.product_price_unit for x in distribution.cost_lines]
            )

    @api.depends("cost_lines", "cost_lines.product_qty")
    def _compute_total_uom_qty(self):
        for distribution in self:
            distribution.total_uom_qty = sum(
                [x.product_qty for x in distribution.cost_lines]
            )

    @api.depends("cost_lines", "cost_lines.total_weight")
    def _compute_total_weight(self):
        for distribution in self:
            distribution.total_weight = sum(
                [x.total_weight for x in distribution.cost_lines]
            )

    @api.depends("cost_lines", "cost_lines.total_volume")
    def _compute_total_volume(self):
        for distribution in self:
            distribution.total_volume = sum(
                [x.total_volume for x in distribution.cost_lines]
            )

    @api.depends("expense_lines", "expense_lines.expense_amount")
    def _compute_total_expense(self):
        for distribution in self:
            distribution.total_expense = sum(
                [x.expense_amount for x in distribution.expense_lines]
            )

    def _expense_lines_default(self):
        expenses = self.env["purchase.expense.type"].search(
            [("default_expense", "=", True)]
        )
        return [{"type": x, "expense_amount": x.default_amount} for x in expenses]

    name = fields.Char(
        string="Distribution number", required=True, index=True, default="/"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency", string="Currency", related="company_id.currency_id"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("calculated", "Calculated"), ("done", "Done")],
        string="Status",
        readonly=True,
        default="draft",
    )
    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        index=True,
        states={"draft": [("readonly", False)]},
        default=fields.Date.context_today,
    )
    total_uom_qty = fields.Float(
        compute=_compute_total_uom_qty,
        readonly=True,
        digits="Product UoS",
        string="Total quantity",
    )
    total_weight = fields.Float(
        compute=_compute_total_weight,
        string="Total gross weight",
        readonly=True,
        digits="Stock Weight",
    )
    total_volume = fields.Float(
        compute=_compute_total_volume, string="Total volume", readonly=True
    )
    total_purchase = fields.Float(
        compute=_compute_total_purchase, digits="Account", string="Total purchase",
    )
    total_price_unit = fields.Float(
        compute=_compute_total_price_unit,
        string="Total price unit",
        digits="Product Price",
    )
    amount_total = fields.Float(
        compute=_compute_amount_total, digits="Account", string="Total",
    )
    total_expense = fields.Float(
        compute=_compute_total_expense, digits="Account", string="Total expenses",
    )
    note = fields.Text(string="Documentation for this order")
    cost_lines = fields.One2many(
        comodel_name="purchase.cost.distribution.line",
        ondelete="cascade",
        inverse_name="distribution",
        string="Distribution lines",
    )
    expense_lines = fields.One2many(
        comodel_name="purchase.cost.distribution.expense",
        ondelete="cascade",
        inverse_name="distribution",
        string="Expenses",
        default=_expense_lines_default,
    )

    def unlink(self):
        for record in self:
            for expense in record.expense_lines:
                moveedistr = self.env['account.move.line'].search(
                    [('distribution_name', '=', expense.distribution_name)])
                acco_movee = self.env['account.move'].browse(expense.invoice_id.id)

                if len(moveedistr) == 1:
                    acco_movee.distribution_name = False

                movee = self.env['account.move.line'].browse(expense.invoice_line.id)
                movee.distribution_id = False
                movee.distribution_name = False
            #
            for costlines in record.cost_lines:
                costlines.picking_id.distribution_id = False
            if record.state not in ('draft', 'calculated'):
                raise UserError(
                    _("You can't delete a confirmed cost distribution"))
        return super(PurchaseCostDistribution, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "purchase.cost.distribution"
            )
        return super(PurchaseCostDistribution, self).create(vals)

    def write(self, vals):
        for command in vals.get("cost_lines", []):

            if command[0] in (2, 3, 5):
                if command[0] == 5:
                    to_check = self.mapped("cost_lines").ids
                else:
                    to_check = [command[1]]
                lines = self.mapped("expense_lines.affected_lines").ids
                if any(i in lines for i in to_check):
                    raise UserError(
                        _(
                            "You can't delete a cost line if it's an "
                            "affected line of any expense line."
                        )
                    )
        return super(PurchaseCostDistribution, self).write(vals)

    @api.model
    def _prepare_expense_line(self, expense_line, cost_line, expenses_type):
        distribution = cost_line.distribution
        if expense_line.type.calculation_method == 'amount':

            multiplier = cost_line.total_amount
            if expense_line.affected_lines:
                divisor = sum([x.total_amount for x in
                               expense_line.affected_lines])
            else:
                divisor = distribution.total_purchase



        elif expense_line.type.calculation_method == 'price':
            multiplier = cost_line.product_price_unit
            if expense_line.affected_lines:
                divisor = sum([x.product_price_unit for x in
                               expense_line.affected_lines])
            else:
                divisor = distribution.total_price_unit
        elif expense_line.type.calculation_method == 'qty':
            multiplier = cost_line.product_qty
            if expense_line.affected_lines:
                divisor = sum([x.product_qty for x in
                               expense_line.affected_lines])
            else:
                divisor = distribution.total_uom_qty
        elif expense_line.type.calculation_method == 'weight':
            multiplier = cost_line.total_weight
            if expense_line.affected_lines:
                divisor = sum([x.total_weight for x in
                               expense_line.affected_lines])
            else:
                divisor = distribution.total_weight
        elif expense_line.type.calculation_method == 'volume':
            multiplier = cost_line.total_volume
            if expense_line.affected_lines:
                divisor = sum([x.total_volume for x in
                               expense_line.affected_lines])
            else:
                divisor = distribution.total_volume
        elif expense_line.type.calculation_method == 'equal':
            multiplier = 1
            divisor = (len(expense_line.affected_lines) or
                       len(distribution.cost_lines))
        else:
            raise UserError(_('No valid distribution type.'))
        if divisor:
            expense_amount = (expense_line.expense_amount * multiplier /
                              divisor)
        else:
            raise UserError(
                _("The cost for the line '%s' can't be "
                  "distributed because the calculation method "
                  "doesn't provide valid data" % expense_line.type.name))
        return {
            'distribution_expense': expense_line.id,
            'expense_amount': expense_amount,
            'cost_ratio': expense_amount / cost_line.product_qty,
            'grup_type_cost': expenses_type.grup_type_cost,
        }

    def action_calculate(self):

        for distribution in self:
            # Check expense lines for amount 0
            if any([not x.expense_amount for x in distribution.expense_lines]):
                raise UserError(
                    _('Please enter an amount for all the expenses'))
            # Check if exist lines in distribution
            if not distribution.cost_lines:
                raise UserError(
                    _('There is no picking lines in the distribution'))
            # Calculating expense line
            for cost_line in distribution.cost_lines:
                cost_line.expense_lines.unlink()
                expense_lines = []
                for expense in distribution.expense_lines:
                    expenses_type = self.env['purchase.expense.type'].search(
                        [('name', '=', expense.type.name), ('cost_active_inactive', '=', True)], limit=1)

                    if (expense.affected_lines and
                            cost_line not in expense.affected_lines):
                        continue
                    expense_lines.append(
                        self._prepare_expense_line(expense, cost_line, expenses_type))
                cost_line.expense_lines = [(0, 0, x) for x in expense_lines]
            distribution.state = 'calculated'
        return True

    def _product_price_update(self, product, vals_list):
        """Method that mimicks stock.move's product_price_update_before_done
        method behaviour, but taking into account that calculations are made
        on an already done moves, and prices sources are given as parameters.
        """
        moves_total_qty = 0
        moves_total_diff_price = 0
        for move, price_diff in vals_list:
            moves_total_qty += move.product_qty
            moves_total_diff_price += move.product_qty * price_diff
        prev_qty_available = product.qty_available - moves_total_qty
        if prev_qty_available <= 0:
            prev_qty_available = 0
        total_available = prev_qty_available + moves_total_qty
        new_std_price = (
                                total_available * product.standard_price + moves_total_diff_price
                        ) / total_available
        # Write the standard price, as SUPERUSER_ID, because a
        # warehouse manager may not have the right to write on products
        product.sudo().write({"standard_price": new_std_price})

    # def action_done(self):
    #     self.ensure_one()
    #     self.state = "done"

    def action_done(self):
        """Perform all moves that touch the same product in batch."""

        self.ensure_one()
        if self.cost_update_type != 'direct':
            return
        d = {}
        for line in self.cost_lines:

            idcurrency = line.purchase_id.currency_id

            distribution = self.env['purchase.cost.distribution'].browse(self.id)
            company = self.env.user.company_id

            cost_date = line.purchase_id.date_order or fields.Date.today()
            price_old = line.product_price_unit_old
            #
            #             price_old = self.currency_id._convert(line.move_id.price_unit, idcurrency, self.company_id, cost_date)

            invoice = self.env['account.move'].search([('invoice_origin', '=', line.picking_id.origin),
                                                       ('state', 'in', ['open', 'paid'])], order='date desc')
            currency_to = distribution.currency_id

            if invoice:
                date = invoice[0].date

                invoice_currency = invoice[0].currency_id
                price_new = self.currency_id._convert(line.standard_price_new, invoice_currency, self.company_id,
                                                      date)

                now = fields.Datetime.now()
                hour = str(now).split(" ")
                date = str(date) + " " + hour[1]

            else:

                if not distribution.tasa_cambio or distribution.tasa_cambio == 0.00:
                    date = cost_date
                    price_new = self.currency_id._convert(line.standard_price_new, idcurrency, self.company_id, date)
                    # price_old = self.currency_id._convert(line.move_id.price_unit, idcurrency, self.company_id,
                    #                                     cost_date)

                else:
                    date = cost_date
                    solicitud_presup = self.env['purchase.order'].browse(line.purchase_id.id)

                    if currency_to != solicitud_presup.currency_id:
                        price_new = line.standard_price_new / distribution.tasa_cambio
                        # price_old = line.move_id.price_unit / distribution.tasa_cambio
                        # price_new = currency_to._convert(result, currency_to, company, cost_date)
                        # _logger.info("estoy debug**********%r" % [line.standard_price_new, price_new, result])
                    else:
                        price_new = line.standard_price_new * 1
                        # result = line.standard_price_new * 1
                        # price_new = currency_to._convert(result, currency_to, company, cost_date)
                        # price_old = line.move_id.price_unit
            price_unit_old_bool = self.env['purchase.order'].browse(line.purchase_id.id)
            #raise UserError(_(round(price_new,9)))
            line.purchase_line_id.write({'price_unit_old': price_old, 'price_unit': round(price_new,9)})
            price_unit_old_bool.price_unit_old_bool = True

            line.picking_id.write({'costed_date': date})

            product = line.move_id.product_id

            if (product.cost_method != 'average' or
                    line.move_id.location_id.usage != 'supplier'):
                continue
            d.setdefault(product, [])
            d[product].append(
                (line.move_id,
                 line.standard_price_new - line.standard_price_old),
            )

            # line.product_price_unit = product_price_unit
        for product, vals_list in d.items():
            self._product_price_update(product, vals_list)
            for move, price_diff in vals_list:
                move.price_unit += price_diff
                # move.value = move.product_uom_qty * move.price_unit

        self.state = 'done'

    def action_draft(self):
        self.ensure_one()
        self.state = "draft"

    def action_cancel(self):
        """Perform all moves that touch the same product in batch."""
        self.ensure_one()
        self.state = 'draft'
        if self.cost_update_type != 'direct':
            return
        d = {}
        for line in self.cost_lines:
            product = line.move_id.product_id
            if (product.cost_method != 'average' or
                    line.move_id.location_id.usage != 'supplier'):
                continue
            if self.currency_id.compare_amounts(
                    line.move_id.price_unit,
                    line.standard_price_new) != 0:
                raise UserError(
                    _('Cost update cannot be undone because there has '
                      'been a later update. Restore correct price and try '
                      'again.'))
            d.setdefault(product, [])
            d[product].append(
                (line.move_id,
                 line.standard_price_old - line.standard_price_new),
            )
        for product, vals_list in d.items():
            self._product_price_update(product, vals_list)
            for move, price_diff in vals_list:
                move.price_unit += price_diff
                # move._run_valuation()


class PurchaseCostDistributionLine(models.Model):
    _name = "purchase.cost.distribution.line"
    _description = "Purchase cost distribution Line"

    @api.depends("product_price_unit", "product_qty")
    def _compute_total_amount(self):
        for dist_line in self:
            dist_line.total_amount = (
                    dist_line.product_price_unit * dist_line.product_qty
            )

    @api.depends("product_id", "product_qty")
    def _compute_total_weight(self):
        for dist_line in self:
            dist_line.total_weight = dist_line.product_weight * dist_line.product_qty

    @api.depends("product_id", "product_qty")
    def _compute_total_volume(self):
        for dist_line in self:
            dist_line.total_volume = dist_line.product_volume * dist_line.product_qty

    @api.depends("expense_lines", "expense_lines.cost_ratio")
    def _compute_cost_ratio(self):
        for dist_line in self:
            dist_line.cost_ratio = sum([x.cost_ratio for x in dist_line.expense_lines])

    @api.depends("expense_lines", "expense_lines.expense_amount")
    def _compute_expense_amount(self):
        for dist_line in self:
            dist_line.expense_amount = sum(
                [x.expense_amount for x in dist_line.expense_lines]
            )

    @api.depends("standard_price_old", "cost_ratio")
    def _compute_standard_price_new(self):
        for dist_line in self:
            dist_line.standard_price_new = (
                    dist_line.standard_price_old + dist_line.cost_ratio
            )

    @api.depends('move_id')
    def _compute_coste_gastos(self):
        for dist_line in self:
            dist_line.coste_gasto = (
                    dist_line.move_id and dist_line.total_amount + dist_line.expense_amount or
                    0.0)

    @api.depends(
        "distribution",
        "distribution.name",
        "picking_id",
        "picking_id.name",
        "product_id",
        "product_id.display_name",
    )
    def _compute_name(self):
        for dist_line in self:
            dist_line.name = "{}: {} / {}".format(
                dist_line.distribution.name,
                dist_line.picking_id.name,
                dist_line.product_id.display_name,
            )

    @api.depends("move_id", "move_id.product_id")
    def _compute_product_id(self):
        for dist_line in self:
            # Cannot be done via related
            # field due to strange bug in update chain
            dist_line.product_id = dist_line.move_id.product_id.id

    @api.depends("move_id", "move_id.product_qty")
    def _compute_product_qty(self):
        for dist_line in self:
            # Cannot be done via related
            #  field due to strange bug in update chain
            dist_line.product_qty = dist_line.move_id.product_qty

    @api.depends("move_id")
    def _compute_standard_price_old(self):
        for dist_line in self:
            #raise UserError(_(dist_line.move_id and dist_line.move_id._get_price_unit() or 0.0))

            dist_line.standard_price_old = (
                    dist_line.move_id and dist_line.move_id._get_price_unit() or 0.0
            )


    name = fields.Char(string="Name", compute="_compute_name", store=True)
    distribution = fields.Many2one(
        comodel_name="purchase.cost.distribution",
        string="Cost distribution",
        ondelete="cascade",
        required=True,
    )

    price = fields.Float(compute='_get_price_unit')

    product_price_unit = fields.Float(
        string='Unit price', digits=(12, 5), related="price")
    product_price_unit_aux = fields.Float(compute='_compute_product_price_unit_aux', digits=(12, 9))

    price_unit_old = fields.Float(digits=(12, 4), compute='_compute_price_unit_old')
    product_price_unit_old = fields.Float(
        string='Old Unit price', compute="_get_product_price_unit_old", digits=(12, 8))

    @api.depends('move_id', 'move_id.product_qty')
    def _compute_product_price_unit_aux(self):
        for dist_line in self:
            try:
                price_unit = dist_line.purchase_line_id.price_unit_vendor_discounted
            except:
                price_unit = dist_line.purchase_line_id.price_unit
            company_id = dist_line.company_id

            if dist_line.distribution.tasa_cambio > 0:
                purchase_order = self.env['purchase.order'].search([('name', '=', dist_line.purchase_id.name)])

                if dist_line.distribution.state == 'done':
                    if purchase_order.currency_id != dist_line.distribution.currency_id:
                        dist_line.product_price_unit_aux = dist_line.purchase_line_id.price_unit_old * dist_line.distribution.tasa_cambio
                    else:
                        dist_line.product_price_unit_aux = dist_line.purchase_line_id.price_unit_old

                else:

                    if purchase_order.currency_id != dist_line.distribution.currency_id:
                        dist_line.product_price_unit_aux = price_unit * dist_line.distribution.tasa_cambio
                    else:
                        dist_line.product_price_unit_aux = price_unit
            else:
                if dist_line.distribution.state == 'done':

                    idcurrency = dist_line.purchase_id.currency_id
                    cost_date = dist_line.purchase_id.date_order or fields.Date.today()

                    dist_line.product_price_unit_aux = idcurrency._convert(dist_line.purchase_line_id.price_unit_old,
                                                                           dist_line.distribution.currency_id,
                                                                           company_id, cost_date)
                else:
                    dist_line.product_price_unit_aux = dist_line.move_id.price_unit

            # raise UserError(_(price_unit))

    @api.depends('move_id', 'move_id.product_qty')
    def _compute_price_unit_old(self):
        for dist_line in self:
            dist_line.price_unit_old = dist_line.purchase_line_id.price_unit_old

    def _get_price_unit(self):
        for dist_line in self:
            try:
                price_unit = dist_line.purchase_line_id.price_unit_vendor_discounted
            except:
                price_unit = dist_line.purchase_line_id.price_unit

            # raise UserError(_(price_unit))

            if dist_line.distribution.tasa_cambio > 0:
                purchase_order = self.env['purchase.order'].search([('name', '=', dist_line.purchase_id.name)])
                if purchase_order.currency_id != dist_line.distribution.currency_id:

                    if dist_line.distribution.state == 'done':

                        dist_line.price = dist_line.purchase_line_id.price_unit_old * dist_line.distribution.tasa_cambio

                        # result = dist_line.purchase_line_id.price_unit_old * dist_line.distribution.tasa_cambio
                        #
                        # company_id = dist_line.company_id
                        # dist_line.price = dist_line.distribution.currency_id._convert(
                        #     result,
                        #     dist_line.distribution.currency_id,
                        #     company_id, dist_line.distribution.date)

                        dist_line.standard_price_old = dist_line.price
                    else:
                        dist_line.price = price_unit * dist_line.distribution.tasa_cambio
                        #
                        # result = price_unit * dist_line.distribution.tasa_cambio
                        #
                        #
                        # company_id = dist_line.company_id
                        # dist_line.price = dist_line.distribution.currency_id._convert(result,
                        #                                                               dist_line.distribution.currency_id,
                        #                                                               company_id,
                        #                                                               dist_line.distribution.date)

                        dist_line.standard_price_old = dist_line.price


                else:
                    if dist_line.distribution.state == 'done':

                        dist_line.price = dist_line.purchase_line_id.price_unit_old * 1
                        # result = dist_line.purchase_line_id.price_unit_old * 1
                        #
                        # company_id = dist_line.company_id
                        # dist_line.price = dist_line.distribution.currency_id._convert(
                        #     result,
                        #     dist_line.distribution.currency_id,
                        #     company_id, dist_line.distribution.date)
                        dist_line.standard_price_old = dist_line.price
                    else:
                        dist_line.price = price_unit * 1
                        # result = price_unit * 1
                        # company_id = dist_line.company_id
                        # dist_line.price = dist_line.distribution.currency_id._convert(result,
                        #                                                               dist_line.distribution.currency_id,
                        #                                                               company_id,
                        #                                                               dist_line.distribution.date)
                        dist_line.standard_price_old = dist_line.price



            else:
                # Cannot be done via related
                #  field due to strange bug in update chain
                invoice = self.env['account.move'].search([('invoice_origin', '=', dist_line.picking_id.origin),
                                                           ('state', 'in', ['open', 'paid'])], order='date desc')
                company_id = dist_line.company_id

                if invoice:

                    date_invoice = invoice[0].date_invoice
                    invoice_currency = invoice[0].currency_id

                    if dist_line.distribution.state == 'done':
                        dist_line.price = invoice_currency._convert(
                            dist_line.purchase_line_id.price_unit_old,
                            dist_line.distribution.currency_id,
                            company_id, date_invoice)
                        dist_line.standard_price_old = dist_line.price
                    else:

                        dist_line.price = invoice_currency._convert(price_unit,
                                                                    dist_line.distribution.currency_id,
                                                                    company_id, date_invoice)
                        dist_line.standard_price_old = dist_line.price
                else:

                    if dist_line.distribution.state == 'done':

                        idcurrency = dist_line.purchase_id.currency_id
                        cost_date = dist_line.purchase_id.date_order or fields.Date.today()

                        dist_line.price = idcurrency._convert(dist_line.purchase_line_id.price_unit_old,
                                                              dist_line.distribution.currency_id,
                                                              company_id, cost_date)
                        dist_line.standard_price_old = dist_line.price
                    else:
                        dist_line.price = dist_line.move_id.price_unit
                        dist_line.standard_price_old = dist_line.price

    def _get_product_price_unit_old(self):

        for dist_line in self:
            try:
                price_unit = dist_line.purchase_line_id.price_unit_vendor_discounted
            except:
                price_unit = dist_line.purchase_line_id.price_unit

            if dist_line.distribution.state == 'done':
                dist_line.product_price_unit_old = 0
            else:
                dist_line.product_price_unit_old = price_unit;

    move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Picking line",
        ondelete="restrict",
        required=True,
    )
    purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Purchase order line",
        related="move_id.purchase_line_id",
    )
    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase order",
        readonly=True,
        related="move_id.purchase_line_id.order_id",
        store=True,
    )
    partner = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        readonly=True,
        related="move_id.purchase_line_id.order_id.partner_id",
    )
    picking_id = fields.Many2one(
        "stock.picking", string="Picking", related="move_id.picking_id", store=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        store=True,
        compute="_compute_product_id",
    )
    product_qty = fields.Float(
        string="Quantity", compute="_compute_product_qty", store=True
    )
    product_uom = fields.Many2one(
        comodel_name="uom.uom", string="Unit of measure", related="move_id.product_uom"
    )
    # product_price_unit = fields.Float(string="Unit price", related="move_id.price_unit")

    expense_lines = fields.One2many(
        comodel_name="purchase.cost.distribution.line.expense",
        inverse_name="distribution_line",
        string="Expenses distribution lines",
    )
    product_volume = fields.Float(
        string="Volume",
        help="The volume in m3.",
        related="product_id.product_tmpl_id.volume",
    )
    product_weight = fields.Float(
        string="Gross weight",
        related="product_id.product_tmpl_id.weight",
        help="The gross weight in Kg.",
    )
    standard_price_old = fields.Float(
        string="Previous cost",
        compute="_compute_standard_price_old",
        store=True,
        digits="Product Price",
    )
    expense_amount = fields.Float(
        string="Cost amount", digits="Account", compute="_compute_expense_amount",
    )
    cost_ratio = fields.Float(string="Unit cost", compute="_compute_cost_ratio")
    standard_price_new = fields.Float(
        string="New cost",
        digits=(12, 5),
        # digits="Product Price",
        compute="_compute_standard_price_new",
    )
    total_amount = fields.Float(
        compute=_compute_total_amount, string="Amount line", digits="Account",
    )
    total_weight = fields.Float(
        compute=_compute_total_weight,
        string="Line weight",
        store=True,
        digits="Stock Weight",
        help="The line gross weight in Kg.",
    )
    total_volume = fields.Float(
        compute=_compute_total_volume,
        string="Line volume",
        store=True,
        help="The line volume in m3.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company", related="distribution.company_id", store=True,
    )

    coste_gasto = fields.Float(string='Costes más Gastos', digits=dp.get_precision('Account'),
                               compute='_compute_coste_gastos')

    @api.model
    def get_action_purchase_cost_distribution(self):
        xml_id = "purchase_landed_cost.action_purchase_cost_distribution"
        action = self.env.ref(xml_id).read()[0]
        distributions = self.mapped("distribution")
        if len(distributions) == 1:
            form = self.env.ref("purchase_landed_cost.purchase_cost_distribution_form")
            action["views"] = [(form.id, "form")]
            action["res_id"] = distributions.id
        else:
            action["domain"] = [("id", "in", distributions.ids)]
        return action

    def unlink(self):
        for record in self:
            record.picking_id.distribution_id = False

        return super(PurchaseCostDistributionLine, self).unlink()


class PurchaseCostDistributionLineExpense(models.Model):
    _name = "purchase.cost.distribution.line.expense"
    _description = "Purchase cost distribution line expense"

    distribution_line = fields.Many2one(
        comodel_name="purchase.cost.distribution.line",
        string="Cost distribution line",
        ondelete="cascade",
    )
    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        store=True,
        readonly=True,
        related="distribution_line.picking_id",
    )
    picking_date_done = fields.Datetime(
        related="picking_id.date_done", store=True, readonly=True,
    )
    distribution_expense = fields.Many2one(
        comodel_name="purchase.cost.distribution.expense",
        string="Distribution expense",
        ondelete="cascade",
    )
    type = fields.Many2one(
        "purchase.expense.type",
        string="Expense type",
        readonly=True,
        related="distribution_expense.type",
        store=True,
    )
    expense_amount = fields.Float(string="Expense amount", digits="Account", )
    cost_ratio = fields.Float("Unit cost")

    company_id = fields.Many2one(
        comodel_name="res.company",
        related="distribution_line.company_id",
        store=True,
        readonly=True,
    )

    grup_type_cost = fields.Char(default=False)
    expence_amount_cal = fields.Char(default=False)


class PurchaseCostDistributionExpense(models.Model):
    _name = "purchase.cost.distribution.expense"
    _description = "Purchase cost distribution expense"
    distribution_id = fields.Char(default=False)
    distribution_name = fields.Char(default=False)

    @api.depends("distribution", "distribution.cost_lines")
    def _compute_imported_lines(self):
        for record in self:
            record.imported_lines = record.env["purchase.cost.distribution.line"]
            record.imported_lines |= record.distribution.cost_lines

    distribution = fields.Many2one(
        comodel_name="purchase.cost.distribution",
        string="Cost distribution",
        index=True,
        ondelete="cascade",
        required=True,
    )
    ref = fields.Char(string="Reference")
    type = fields.Many2one(
        comodel_name="purchase.expense.type",
        string="Expense type",
        index=True,
        ondelete="restrict",
    )
    calculation_method = fields.Selection(
        string="Calculation method", related="type.calculation_method", readonly=True
    )
    imported_lines = fields.Many2many(
        comodel_name="purchase.cost.distribution.line",
        string="Imported lines",
        compute="_compute_imported_lines",
    )
    affected_lines = fields.Many2many(
        comodel_name="purchase.cost.distribution.line",
        column1="expense_id",
        relation="distribution_expense_aff_rel",
        column2="line_id",
        string="Affected lines",
        help="Put here specific lines that this expense is going to be "
             "distributed across. Leave it blank to use all imported lines.",
        domain="[('id', 'in', imported_lines)]",
    )
    expense_amount = fields.Float(
        string='Expense amount', digits=dp.get_precision('Account'), compute="_compute_expense_amount",
        required=True, readonly=True)
    invoice_id = fields.Many2one(comodel_name="account.move", string="Invoice")
    invoice_line = fields.Many2one(
        comodel_name="account.move.line",
        string="Supplier invoice line",
        domain="[('invoice_id.move_type', '=', 'in_invoice'),('invoice_id.state', '=', 'posted')]"
    )

    # _columns = {
    #     'invoice_line': fields.many2one('account.move.line', 'Supplier invoice line', domain="[('invoice_id.move_type', '=', 'in_invoice'),('invoice_id.state', '=', 'posted')]"),
    #
    # }

    # _columns = {
    #
    #     'invoice_id': fields.many2one('account.move', 'Invoice'),
    #
    # }
    display_name = fields.Char(compute="_compute_display_name", store=True)
    company_id = fields.Many2one(
        comodel_name="res.company", related="distribution.company_id", store=True,
    )

    def _compute_expense_amount(self):
        for expense_lines in self:
            amount = expense_lines.invoice_line.price_subtotal
            distribution = self.env['purchase.cost.distribution'].browse(expense_lines.distribution.id)
            currency_to = expense_lines.distribution.currency_id
            company = distribution.company_id or self.env.user.company_id
            cost_date = expense_lines.invoice_id.date or fields.Date.today()
            facturas = self.env['account.move'].browse(expense_lines.invoice_id.id)

            if currency_to != facturas.currency_id:
                result = amount * distribution.tasa_cambio
                expense_lines.expense_amount = currency_to._convert(result, currency_to, company, cost_date)

            else:
                result = amount * 1
                expense_lines.expense_amount = currency_to._convert(result, currency_to, company, cost_date)

    @api.depends("distribution", "type", "expense_amount", "ref")
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{}: {} - {} ({})".format(
                record.distribution.name,
                record.type.name,
                record.ref,
                formatLang(
                    record.env,
                    record.expense_amount,
                    currency_obj=record.distribution.currency_id,
                ),
            )

    @api.onchange("type")
    def onchange_type(self):
        """set expense_amount in the currency of the distribution"""
        if self.type and self.type.default_amount:
            currency_from = self.type.company_id.currency_id
            amount = self.type.default_amount
            currency_to = self.distribution.currency_id
            company = self.company_id or self.env.user.company_id
            cost_date = self.distribution.date or fields.Date.today()
            self.expense_amount = currency_from._convert(
                amount, currency_to, company, cost_date
            )

    @api.onchange("invoice_line")
    def onchange_invoice_line(self):
        _logger.info("estoyOsmel debug**********%r" % [self.invoice_id])
        """set expense_amount in the currency of the distribution"""
        self.invoice_id = self.invoice_line.invoice_id.id

        currency_from = self.invoice_line.company_id.currency_id
        amount = self.invoice_line.price_subtotal
        currency_to = self.distribution.currency_id
        company = self.company_id or self.env.user.company_id
        cost_date = self.distribution.date or fields.Date.today()
        self.expense_amount = currency_from._convert(
            amount, currency_to, company, cost_date
        )

    @api.depends('account.move.line')
    def unlink(self):

        for record in self:
            moveedistr = self.env['account.move.line'].search([('distribution_name', '=', record.distribution_name)])

            if len(self.invoice_id) > 1:
                for invo in self.invoice_id:
                    acco_movee = self.env['account.move'].browse(invo.id)
                    if len(moveedistr) == 1:
                        acco_movee.distribution_name = False

            else:
                acco_movee = self.env['account.move'].browse(self.invoice_id.id)
                if len(moveedistr) == 1:
                    acco_movee.distribution_name = False

            movee = self.env['account.move.line'].browse(record.invoice_line.id)

            movee.distribution_name = False
            movee.distribution_id = False

        return super(PurchaseCostDistributionExpense, self).unlink()

    def button_duplicate(self):
        for expense in self:
            expense.copy()


class StockMovePrueba(models.Model):
    _inherit = "stock.move"

    def _run_valuation(self, quantity=None):
        self.ensure_one()
        value_to_return = 0
        if self._is_in():
            valued_move_lines = self.move_line_ids.filtered(lambda
                                                                ml: not ml.location_id._should_be_valued() and ml.location_dest_id._should_be_valued() and not ml.owner_id)
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,
                                                                                     self.product_id.uom_id)

            # Note: we always compute the fifo `remaining_value` and `remaining_qty` fields no
            # matter which cost method is set, to ease the switching of cost method.
            vals = {}
            price_unit = self._get_price_unit()
            value = price_unit * (quantity or valued_quantity)
            value_to_return = value if quantity is None or not self.value else self.value
            vals = {
                'price_unit': price_unit,
                'value': value_to_return,
                'remaining_value': value if quantity is None else self.remaining_value + value,
            }
            vals['remaining_qty'] = valued_quantity if quantity is None else self.remaining_qty + quantity

            if self.product_id.cost_method == 'standard':
                value = self.product_id.standard_price * (quantity or valued_quantity)
                value_to_return = value if quantity is None or not self.value else self.value
                vals.update({
                    'price_unit': self.product_id.standard_price,
                    'value': value_to_return,
                })
            self.write(vals)
        elif self._is_out():
            valued_move_lines = self.move_line_ids.filtered(lambda
                                                                ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,
                                                                                     self.product_id.uom_id)
            self.env['stock.move']._run_fifo(self, quantity=quantity)
            if self.product_id.cost_method in ['standard', 'average']:
                curr_rounding = self.company_id.currency_id.rounding
                value = -float_round(
                    self.product_id.standard_price * (valued_quantity if quantity is None else quantity),
                    precision_rounding=curr_rounding)
                value_to_return = value if quantity is None else self.value + value
                self.write({
                    'value': value_to_return,
                    'price_unit': value / valued_quantity,
                })
        elif self._is_dropshipped() or self._is_dropshipped_returned():
            curr_rounding = self.company_id.currency_id.rounding
            if self.product_id.cost_method in ['fifo']:
                price_unit = self._get_price_unit()
                # see test_dropship_fifo_perpetual_anglosaxon_ordered
                self.product_id.standard_price = price_unit
            else:
                price_unit = self.product_id.standard_price
            value = float_round(self.product_qty * price_unit, precision_rounding=curr_rounding)
            value_to_return = value if self._is_dropshipped() else -value
            # In move have a positive value, out move have a negative value, let's arbitrary say
            # dropship are positive.
            self.write({
                'value': value_to_return,
                'price_unit': price_unit if self._is_dropshipped() else -price_unit,
            })
        return value_to_return