# -*- coding: utf-8 -*-
# from odoo import http


# class L10nNiReportesVet(http.Controller):
#     @http.route('/l10n_ni_reportes_vet/l10n_ni_reportes_vet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_ni_reportes_vet/l10n_ni_reportes_vet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_ni_reportes_vet.listing', {
#             'root': '/l10n_ni_reportes_vet/l10n_ni_reportes_vet',
#             'objects': http.request.env['l10n_ni_reportes_vet.l10n_ni_reportes_vet'].search([]),
#         })

#     @http.route('/l10n_ni_reportes_vet/l10n_ni_reportes_vet/objects/<model("l10n_ni_reportes_vet.l10n_ni_reportes_vet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_ni_reportes_vet.object', {
#             'object': obj
#         })
