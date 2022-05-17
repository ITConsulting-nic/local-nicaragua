# -*- coding: utf-8 -*-
from odoo import http

# class ReportAsientosContablesPdf(http.Controller):
#     @http.route('/report_asientos_contables_pdf/report_asientos_contables_pdf/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_asientos_contables_pdf/report_asientos_contables_pdf/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_asientos_contables_pdf.listing', {
#             'root': '/report_asientos_contables_pdf/report_asientos_contables_pdf',
#             'objects': http.request.env['report_asientos_contables_pdf.report_asientos_contables_pdf'].search([]),
#         })

#     @http.route('/report_asientos_contables_pdf/report_asientos_contables_pdf/objects/<model("report_asientos_contables_pdf.report_asientos_contables_pdf"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_asientos_contables_pdf.object', {
#             'object': obj
#         })