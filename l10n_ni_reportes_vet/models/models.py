# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class l10n_ni_reportes_vet(models.Model):
#     _name = 'l10n_ni_reportes_vet.l10n_ni_reportes_vet'
#     _description = 'l10n_ni_reportes_vet.l10n_ni_reportes_vet'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
