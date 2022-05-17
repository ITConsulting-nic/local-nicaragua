# -*- coding: utf-8 -*-
# Copyright (C) 2017-present  Technaureus Info Solutions(<http://www.technaureus.com/>).
from odoo import api, fields, models, _

class AccountTax(models.Model):
    _inherit = 'account.tax'
    
    tds = fields.Boolean('Retención', default=False)
    journal_id = fields.Many2one('account.journal', string='Diario de retenciones')
    #payment_excess = fields.Float('Payment in excess of')


