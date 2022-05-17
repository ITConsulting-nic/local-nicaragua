
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


import logging
_logger = logging.getLogger(__name__)

class RetentionMoveWizard(models.TransientModel):

    _name = 'retention.move.wizard'

    invoice_name = fields.Char(string='Nombre de la Factura')
    invoice_date = fields.Date(string='Fecha de la Factura')
    date = fields.Date(string='Fecha contable de retención', default=fields.Date.context_today)
    invoice = fields.Many2one('account.move', string='Factura')
    #moveields.Char()


    @api.model
    def default_get(self, fields):
        res = super(RetentionMoveWizard, self).default_get(fields)

        invoice = self.env['account.move'].browse(self.env.context['active_id'])
        
        if 'invoice_name' in fields:
            res['invoice_name'] = invoice.name
        if 'invoice_date' in fields:
            res['invoice_date'] = invoice.date
        if 'move_type' in fields:
            res['move_type'] = invoice.move_type
        if 'invoice' in fields:
            res['invoice'] = invoice.id

        return res

    def add_retention(self):

        #invoice = self.env['account.move'].browse(self.env.context['active_id'])

        if self.invoice.move_type == 'out_invoice':
            self.add_retention_client()
        elif self.invoice.move_type == 'in_invoice':
            self.add_retention_supplier()
        
        self.invoice.tds = True
    
    def add_retention_client(self):
    
        for tds in self.invoice.apliqued_witholding:

            AccountMove = self.env['account.move']
            lines_ids = []
            

            tax = self.env['account.tax'].search([('id', '=', tds.code)])
            #amount_currency = self.invoice.currency_id._convert(tds.tds_amount, self.invoice.company_id.currency_id, self.invoice.company_id, self.invoice_date)

            #_logger.info("adscdvn %s" % [tax, tds, tds.tax, tds.tds_amount, tds.code])
            aux = 0.0
            for element in tax.invoice_repartition_line_ids:
                if element.repartition_type == 'tax':
                    tax_amount = tds.tds_amount * element.factor
                    aux+= tax_amount

                    debit_line = (0, 0, {
                        'name': _('%s Asiento de retención %s - RET %s') % (
                            self.env.user.name, self.invoice_name, tax.name),
                        'account_id': element.account_id.id,
                        'journal_id': tax.journal_id.id,
                        'debit': abs(tax_amount),
                        'credit': 0,
                    })

                    lines_ids.append(debit_line)

            credit_line =  (0, 0, {
                        'name': _('%s Asiento por retención %s - RET %s') % (
                            self.env.user.name, self.invoice_name, tax.name),
                        'account_id': self.invoice.partner_id.property_account_receivable_id.id,
                        'partner_id': self.invoice.partner_id.id,
                        'journal_id': tax.journal_id.id,
                        'debit': 0,
                        'credit': abs(aux),
                    })

            lines_ids.append(credit_line)

            move_vals = {
                'journal_id': tax.journal_id.id,
                'date': self.date,
                'company_id': self.invoice.company_id.id,
                'ref': "Retención " + tax.name,
                'partner_id': self.invoice.partner_id.id,
                'move_type': 'entry',
                'line_ids': lines_ids,
            }

            move = AccountMove.create(move_vals)
            move.invoice_name = self.invoice_name
            move.post()

    def add_retention_supplier(self):

        for tds in self.invoice.apliqued_witholding:

            AccountMove = self.env['account.move']
            lines_ids = []

            tax = self.env['account.tax'].search([('id', '=', tds.code)])      
            #amount_currency = self.invoice.currency_id._convert(tds.tds_amount, self.invoice.company_id.currency_id, self.invoice.company_id, self.invoice_date)
            
            aux = 0.0
            for element in tax.invoice_repartition_line_ids:
                if element.repartition_type == 'tax':
                    tax_amount = tds.tds_amount * element.factor
                    aux += tax_amount

                    credit_line = (0, 0, {
                        'name': _('%s Asiento de retención %s - RET %s ') % (
                            self.env.user.name, self.invoice_name, tax.name),
                        'account_id': element.account_id.id,
                        'journal_id': tax.journal_id.id,
                        'debit': 0,
                        'credit': abs(tax_amount),
                    })

                    lines_ids.append(credit_line)

            debit_line = (0, 0, {
                'name': _('%s Asiento por retención %s - RET %s') % (
                    self.env.user.name, self.invoice_name, tax.name),
                'account_id': self.invoice.partner_id.property_account_payable_id.id,
                'partner_id': self.invoice.partner_id.id,
                'journal_id': tax.journal_id.id,
                'debit': abs(aux),
                'credit': 0,
            })

            lines_ids.append(debit_line)

            move_vals = {
                'journal_id': tax.journal_id.id,
                'date': self.date,
                'company_id': self.invoice.company_id.id,
                'ref': "Retención " + tax.name,
                'partner_id': self.invoice.partner_id.id,
                'move_type': 'entry',
                'line_ids': lines_ids,
            }

            move = AccountMove.create(move_vals)
            move.invoice_name = self.invoice_name
            move.post()
