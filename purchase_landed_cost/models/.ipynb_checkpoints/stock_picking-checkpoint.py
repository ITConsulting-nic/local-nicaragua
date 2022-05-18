# Copyright 2013 Joaquín Gutierrez
# Copyright 2014-2016 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3
from odoo import api, models, fields, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    costed_date = fields.Datetime('Fecha de costeo')

    @api.multi
    def action_open_landed_cost(self):
        self.ensure_one()
        line_obj = self.env['purchase.cost.distribution.line']
        lines = line_obj.search([('picking_id', '=', self.id)])
        if lines:
            return lines.get_action_purchase_cost_distribution()

    def _get_product_accounts(self):

        accounts = {}

        for order in self.purchase_id.order_line:

            if order.product_id.type == 'product':

                product_accounts = {order.product_id: order.product_id.product_tmpl_id.get_product_accounts()}

                account_id = product_accounts[order.product_id]['stock_input'].id
                stock_journal = product_accounts[order.product_id]['stock_journal'].id

                key = (account_id, stock_journal)

                if key not in accounts:

                    accounts[key] = order.price_unit
                else:
                    accounts[key] += order.price_unit

            print("precio unitario y producto %r " % [order.price_unit, order.product_id, product_accounts])

        return accounts

    @api.multi
    def button_validate(self):

        AccountMove = self.env['account.move']

        res = super(StockPicking, self).button_validate()

        current_date = fields.Datetime.now()

        print("FECHAHHAHAHAHAH %r " % [str(current_date).split(" ")[0], str(self.costed_date).split(" ")[0]])

        if self.company_id.currency_id != self.purchase_id.currency_id:

            if str(current_date).split(" ")[0] != str(self.costed_date).split(" ")[0]:

                if self.costed_date:

                    stock_accounst = self._get_product_accounts()

                    for acount in stock_accounst:

                        amount = stock_accounst[acount]

                        amount_costed = self.purchase_id.currency_id._convert(amount,
                                                                              self.company_id.currency_id,
                                                                              self.company_id, self.costed_date)

                        current_amount = self.purchase_id.currency_id._convert(amount,
                                                                               self.company_id.currency_id,
                                                                               self.company_id, current_date)

                        diff = current_amount - amount_costed

                        diff = self.company_id.currency_id._convert(diff,
                                                                    self.company_id.currency_id,
                                                                    self.company_id, current_date)

                        print("MONTOS %r" % [amount_costed, current_amount, diff])

                        if diff > 0:
                            debit_account_id = acount[0]
                            credit_account_id = self.company_id.currency_exchange_journal_id.default_credit_account_id.id
                        else:
                            debit_account_id = self.company_id.currency_exchange_journal_id.default_debit_account_id.id
                            credit_account_id = acount[0]

                        move_vals = {
                            'journal_id': self.company_id.currency_exchange_journal_id.id,
                            'company_id': self.company_id.id,
                            'ref': self.name,
                            'line_ids': [(0, 0, {
                                'name': _('%s Asiento por diferencial %s ') % (
                                    self.env.user.name, self.name),
                                'account_id': debit_account_id,
                                'debit': abs(diff),
                                'credit': 0,

                            }), (0, 0, {
                                'name': _('%s Asiento por diferencial %s ') % (
                                    self.env.user.name, self.name),
                                'account_id': credit_account_id,
                                'debit': 0,
                                'credit': abs(diff),

                            })],
                        }
                        move = AccountMove.create(move_vals)
                        move.post()

        return res
