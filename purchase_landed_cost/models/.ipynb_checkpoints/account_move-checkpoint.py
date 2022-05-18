from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        """ :context's key `check_move_validity`: check data consistency after move line creation. Eg. set to false to disable verification that the move
                debit-credit == 0 while creating the move lines composing the move.
        """

        print("VALS en move account%r" % vals_list)

        for vals in vals_list:

            account = self.env['account.account'].browse(vals['account_id'])

            amount = vals.get('debit', 0.0) - vals.get('credit', 0.0)
            move = self.env['account.move'].browse(vals['move_id'])

            picking = self.env['stock.picking'].search([('name', '=', move.ref), ('costed_date', '!=', False)])

            print("Costed Date%r" % picking.costed_date)

            if picking.costed_date:
                if 'amount_currency' in vals:

                    currcy = self.env['res.currency'].browse(vals['currency_id'])

                    if vals['credit'] != 0.0:
                        credito = currcy._convert(vals['amount_currency'], account.company_id.currency_id,
                                                  account.company_id, picking.costed_date)
                        vals['credit'] = abs(credito)

                    if vals['debit'] != 0.0:
                        debito = currcy._convert(vals['amount_currency'], account.company_id.currency_id,
                                                 account.company_id, picking.costed_date)
                        vals['debit'] = abs(debito)

        #     if account.deprecated:
        #         raise UserError(_('The account %s (%s) is deprecated.') % (account.name, account.code))
        #     journal = vals.get('journal_id') and self.env['account.journal'].browse(
        #         vals['journal_id']) or move.journal_id
        #     vals['date_maturity'] = vals.get('date_maturity') or vals.get('date') or move.date
        #
        #     ok = (
        #             (not journal.type_control_ids and not journal.account_control_ids)
        #             or account.user_type_id in journal.type_control_ids
        #             or account in journal.account_control_ids
        #     )
        #     if not ok:
        #         raise UserError(_(
        #             'You cannot use this general account in this journal, check the tab \'Entry Controls\' on the related journal.'))
        #
        #     # Automatically convert in the account's secondary currency if there is one and
        #     # the provided values were not already multi-currency
        #     if account.currency_id and 'amount_currency' not in vals and account.currency_id.id != account.company_id.currency_id.id:
        #         vals['currency_id'] = account.currency_id.id
        #
        #         date = vals.get('date') or vals.get('date_maturity') or fields.Date.today()
        #         vals['amount_currency'] = account.company_id.currency_id._convert(amount, account.currency_id,
        #                                                                           account.company_id, date)
        #
        #     # print("VALS en moneda BASEEEE move account%r" % vals)
        #     # Toggle the 'tax_exigible' field to False in case it is not yet given and the tax in 'tax_line_id' or one of
        #     # the 'tax_ids' is a cash based tax.
        #     taxes = False
        #     if vals.get('tax_line_id'):
        #         taxes = [{'tax_exigibility': self.env['account.tax'].browse(vals['tax_line_id']).tax_exigibility}]
        #     if vals.get('tax_ids'):
        #         taxes = self.env['account.move.line'].resolve_2many_commands('tax_ids', vals['tax_ids'])
        #     if taxes and any([tax['tax_exigibility'] == 'on_payment' for tax in taxes]) and not vals.get(
        #             'tax_exigible'):
        #         vals['tax_exigible'] = False
        #
        # lines = super(AccountMoveLine, self).create(vals_list)
        #
        # # print("VALS en move account2%r" % lines)
        #
        # if self._context.get('check_move_validity', True):
        #     lines.mapped('move_id')._post_validate()
        #
        #     # print("VALS en move account22222%r" % lines)

        return super(AccountMoveLine, self).create(vals_list)
