# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class l10n_ni_formatos_dgi(models.Model):
#     _name = 'l10n_ni_formatos_dgi.l10n_ni_formatos_dgi'
#     _description = 'l10n_ni_formatos_dgi.l10n_ni_formatos_dgi'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import json
from datetime import datetime

_logger = logging.getLogger(__name__)



class AccountInvoice(models.Model):
    _inherit = "account.move"

    def external_layout_aux(self, aux):
        result = "false"
        if aux == "nota_credito":
            campo = self.env['ir.config_parameter'].sudo().get_param('l10n_ni_formatos_dgi.nota_credito')
            # etc = self.env['ir.config_parameter'].sudo().get_param('l10n_ni_formatos_dgi.etc')
            if campo:
                result = "true"
            else:
                result = "false"

        if aux == "nota_debito":
            campo = self.env['ir.config_parameter'].sudo().get_param('l10n_ni_formatos_dgi.nota_debito')
            # etc = self.env['ir.config_parameter'].sudo().get_param('l10n_ni_formatos_dgi.etc')
            if campo:
                result = "true"
            else:
                result = "false"

        if aux == "factura":
            campo = self.env['ir.config_parameter'].sudo().get_param('l10n_ni_formatos_dgi.factura_venta')
            # etc = self.env['ir.config_parameter'].sudo().get_param('l10n_ni_formatos_dgi.etc')
            if campo:
                result = "true"
            else:
                result = "false"

        return result

    def invoice_payments_widget_aux(self, o):

        data = json.loads(o.invoice_payments_widget)

        # _logger.info("estoy debug**********%r" % ["Siiiii"])
        # _logger.info("estoy debug**********%r" % [data])
        # _logger.info("estoy debug**********%r" % ["Siiiii"])
        # for dat in data['content']:
        #     dat['date'] = datetime.datetime.strptime(dat['date'], '%Y-%m-%d')
        #     _logger.info("estoy debug**********%r" % ["Siiii11111i"])
        #     _logger.info("estoy debug**********%r" % [dat])
        #     _logger.info("estoy debug**********%r" % ["Siiii111111i"])
        return data['content']

    def getRetencionesAux(self, retenciones):
        cadena = ""
        for aux in retenciones:
            if cadena == "":
                cadena = aux.name
            else:
                cadena = cadena + ", "+ aux.name
        return  cadena


class DebitoReport(models.TransientModel):
    _name = 'reports.report_credito_template'

    @api.model
    def get_report_values(self, docids, data=None):

        docs = []
        docs = self.env['account.move'].browse(
            self._context.get('active_id'))

        return {
            'doc_ids': docids,
            'doc_model': 'model.name',
            'docs': docs,
            'data': data,
        }




class DebitoReport(models.TransientModel):
    _name = 'reports.report_credito_template'

    @api.model
    def get_report_values(self, docids, data=None):

        docs = []
        docs = self.env['account.move'].browse(
            self._context.get('active_id'))

        return {
            'doc_ids': docids,
            'doc_model': 'model.name',
            'docs': docs,
            'data': data,
        }


class DebitoReport(models.TransientModel):
    _name = 'reports.report_dianca_template'

    @api.model
    def get_report_values(self, docids, data=None):

        docs = []
        docs = self.env['account.move'].browse(
            self._context.get('active_id'))

        return {
            'doc_ids': docids,
            'doc_model': 'model.name',
            'docs': docs,
            'data': data,
        }


class AccountPayment(models.Model):
    _inherit = "account.payment"

    check_no = fields.Char(string='Cheque No.')
    bank_is = fields.Many2one('res.bank', string='Banco')
    card_is = fields.Char(string='Tarjeta No.')
    pago_type = fields.Selection(
        [('cash', 'Efectivo'), ('check', 'Cheque'), ('card', 'Tarjeta')],
        string="Método de pago")


    def external_layout_aux(self, aux):
        result = "false"
        if aux == "recibo_caja":
            campo = self.env['ir.config_parameter'].sudo().get_param('l10n_ni_formatos_dgi.recibo_caja')
            etc = self.env['ir.config_parameter'].sudo().get_param('l10n_ni_formatos_dgi.etc')
            if campo or etc:
                result = "true"
            else:
                result = "false"

        return result


class CustomReport(models.TransientModel):

    _name = 'reports.report_custom_template'

    @api.model
    def get_report_values(self, docids, data=None):

        docs = []
        docs = self.env['account.payment'].browse(
            self._context.get('active_id'))

        return {
            'doc_ids': docids,
            'doc_model': 'model.name',
            'docs': docs,
            'data': data,
        }