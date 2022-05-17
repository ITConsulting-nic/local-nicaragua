# -*- coding: utf-8 -*-
# from odoo import http


# class WitholdingNic(http.Controller):
#     @http.route('/witholding_nic/witholding_nic/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/witholding_nic/witholding_nic/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('witholding_nic.listing', {
#             'root': '/witholding_nic/witholding_nic',
#             'objects': http.request.env['witholding_nic.witholding_nic'].search([]),
#         })

#     @http.route('/witholding_nic/witholding_nic/objects/<model("witholding_nic.witholding_nic"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('witholding_nic.object', {
#             'object': obj
#         })
