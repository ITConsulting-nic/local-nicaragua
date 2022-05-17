# -*- coding: utf-8 -*-
# from odoo import http


# class L10nNiFormatosDgi(http.Controller):
#     @http.route('/l10n_ni_formatos_dgi/l10n_ni_formatos_dgi/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_ni_formatos_dgi/l10n_ni_formatos_dgi/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_ni_formatos_dgi.listing', {
#             'root': '/l10n_ni_formatos_dgi/l10n_ni_formatos_dgi',
#             'objects': http.request.env['l10n_ni_formatos_dgi.l10n_ni_formatos_dgi'].search([]),
#         })

#     @http.route('/l10n_ni_formatos_dgi/l10n_ni_formatos_dgi/objects/<model("l10n_ni_formatos_dgi.l10n_ni_formatos_dgi"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_ni_formatos_dgi.object', {
#             'object': obj
#         })
