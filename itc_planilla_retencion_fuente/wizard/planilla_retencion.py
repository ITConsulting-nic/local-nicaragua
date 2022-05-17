# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

import base64
import logging
import tempfile
from odoo import models, exceptions, fields, api, _
import logging as _logger
from datetime import date

try:
    import xlsxwriter
except ImportError:
    _logger.warning("Cannot import xlsxwriter")
    xlsxwriter = False


class fichamaestra(models.TransientModel):
    _name = "itc.planilla.retencion.report"

    def find_rule_value(self, list, code):
        sol = 0
        for lines in list:
            if lines.code == code:
                sol = lines.total
                break
        return sol

    def print_excel_report(self):
        if not xlsxwriter:
            raise UserError(_("The Python library xlsxwriter is installed. Contact your system administrator"))

        payslips = self.env.context.get('active_ids')

        file_path = tempfile.mktemp(suffix='.xlsx')
        workbook = xlsxwriter.Workbook(file_path)
        styles = {
            'main_data': workbook.add_format({
                'font_size': 9,
                'border': 1,
                'bold': False,
                'num_format': '#,##0.00',
            }),
            'main_data_bold': workbook.add_format({
                'font_size': 9,
                'border': 1,
                'bold': True,
                'bg_color': '#B7DEE8'
            }),
            'main_data_date': workbook.add_format({
                'font_size': 9,
                'border': 1,
                'bold': False,
                'num_format': 'mm/dd/yyyy',
            }),
        }

        worksheet = workbook.add_worksheet("Planilla_Retenciones_en_la_Fuente")
        worksheet.set_column(0, 0, 35)
        worksheet.set_column(1, 1, 35)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 20)
        worksheet.set_column(4, 4, 20)
        worksheet.set_column(5, 5, 20)
        worksheet.set_column(6, 6, 20)
        worksheet.set_column(7, 7, 20)
        worksheet.set_column(8, 8, 20)
        worksheet.set_column(9, 9, 20)
        worksheet.set_column(9, 9, 20)
        worksheet.set_column(10, 10, 20)

        worksheet.write(0, 0, "No. RUC", styles.get("main_data_bold"))
        worksheet.write(0, 1, "NOMBRE Y APELLIDOS Ó RAZÓN SOCIAL", styles.get("main_data_bold"))
        worksheet.write(0, 2, "INGRESOS BRUTOS MENSUALES", styles.get("main_data_bold"))
        worksheet.write(0, 3, "VALOR COTIZACIÓN INSS", styles.get("main_data_bold"))
        worksheet.write(0, 4, "VALOR FONDO PENSIONES AHORRO", styles.get("main_data_bold"))
        worksheet.write(0, 5, "NÚMERO DE DOCUMENTO", styles.get("main_data_bold"))
        worksheet.write(0, 6, "FECHA DE DOCUMENTO", styles.get("main_data_bold"))
        worksheet.write(0, 7, "BASE IMPONIBLE", styles.get("main_data_bold"))
        worksheet.write(0, 8, "VALOR RETENIDO", styles.get("main_data_bold"))
        worksheet.write(0, 9, "ALÍCUOTA DE RETENCIÓN", styles.get("main_data_bold"))
        worksheet.write(0, 10, "CÓDIGO DE RETENCIÓN", styles.get("main_data_bold"))

        if payslips:
            dict_employee_name = dict()
            for payslip in payslips:
                procesamiento = self.env['hr.payslip.run'].browse(payslip)
                if procesamiento:
                    for slip in procesamiento.slip_ids:
                        dict_slip = {'No. RUC': slip.employee_id.num_cedula or "",
                                     'NOMBRE Y APELLIDOS Ó RAZÓN SOCIAL': slip.employee_id.name or "",
                                     'INGRESOS BRUTOS MENSUALES': self.find_rule_value(slip.line_ids, "GROSS"),
                                     'VALOR COTIZACIÓN INSS': self.find_rule_value(slip.line_ids, "DED201"),
                                     'VALOR FONDO PENSIONES AHORRO': "",
                                     'NÚMERO DE DOCUMENTO': "",
                                     'FECHA DE DOCUMENTO': str(date.today()),
                                     'BASE IMPONIBLE': self.find_rule_value(slip.line_ids,
                                                                            "GROSS") - self.find_rule_value(
                                         slip.line_ids, "DED201"),
                                     'VALOR RETENIDO': self.find_rule_value(slip.line_ids, "DED204"),
                                     'ALÍCUOTA DE RETENCIÓN': "",
                                     'CÓDIGO DE RETENCIÓN': "11"
                                     }
                        if slip.employee_id.name in dict_employee_name:
                            dict_employee_name[slip.employee_id.name].update({'INGRESOS BRUTOS MENSUALES':
                                                                                  dict_employee_name[
                                                                                      slip.employee_id.name].get(
                                                                                      "INGRESOS BRUTOS MENSUALES") + dict_slip.get(
                                                                                      "INGRESOS BRUTOS MENSUALES"),
                                                                              'VALOR COTIZACIÓN INSS':
                                                                                  dict_employee_name[
                                                                                      slip.employee_id.name].get(
                                                                                      "VALOR COTIZACIÓN INSS") + dict_slip.get(
                                                                                      "VALOR COTIZACIÓN INSS"),
                                                                              'BASE IMPONIBLE': dict_employee_name[
                                                                                                    slip.employee_id.name].get(
                                                                                  "BASE IMPONIBLE") + dict_slip.get(
                                                                                  "BASE IMPONIBLE"),
                                                                              'VALOR RETENIDO': dict_employee_name[
                                                                                                    slip.employee_id.name].get(
                                                                                  "VALOR RETENIDO") + dict_slip.get(
                                                                                  "VALOR RETENIDO")})
                        else:
                            dict_employee_name[slip.employee_id.name] = dict_slip
                    col = 0
            for name in dict_employee_name:
                col += 1
                worksheet.write(col, 0, dict_employee_name[name].get("No. RUC"), styles.get("main_data"))
                worksheet.write(col, 1, dict_employee_name[name].get("NOMBRE Y APELLIDOS Ó RAZÓN SOCIAL"),
                                styles.get("main_data"))
                if dict_employee_name[name].get("INGRESOS BRUTOS MENSUALES") == 0:
                    worksheet.write(col, 2, "", styles.get("main_data"))
                else:
                    worksheet.write(col, 2, dict_employee_name[name].get("INGRESOS BRUTOS MENSUALES"),
                                    styles.get("main_data"))
                if dict_employee_name[name].get("VALOR COTIZACIÓN INSS") == 0:
                    worksheet.write(col, 3, "", styles.get("main_data"))
                else:
                    worksheet.write(col, 3, dict_employee_name[name].get("VALOR COTIZACIÓN INSS"),
                                    styles.get("main_data"))
                worksheet.write(col, 4, dict_employee_name[name].get("VALOR FONDO PENSIONES AHORRO"),
                                styles.get("main_data"))
                worksheet.write(col, 5, dict_employee_name[name].get("NÚMERO DE DOCUMENTO"), styles.get("main_data"))
                worksheet.write(col, 6, dict_employee_name[name].get("FECHA DE DOCUMENTO"), styles.get("main_data_date"))
                if dict_employee_name[name].get("BASE IMPONIBLE") == 0:
                    worksheet.write(col, 7, "", styles.get("main_data"))
                else:
                    worksheet.write(col, 7, dict_employee_name[name].get("BASE IMPONIBLE"), styles.get("main_data"))
                if dict_employee_name[name].get("VALOR RETENIDO") == 0:
                    worksheet.write(col, 8, "", styles.get("main_data"))
                else:
                    worksheet.write(col, 8, dict_employee_name[name].get("VALOR RETENIDO"), styles.get("main_data"))
                worksheet.write(col, 9, dict_employee_name[name].get("ALÍCUOTA DE RETENCIÓN"), styles.get("main_data"))
                worksheet.write(col, 10, dict_employee_name[name].get("CÓDIGO DE RETENCIÓN"), styles.get("main_data"))

        workbook.close()
        with open(file_path, 'rb') as r:
            xls_file = base64.b64encode(r.read())
        att_vals = {
            'name': u"{}#{}.xlsx".format("Planilla_Retenciones_en_la_Fuente", fields.Date.today()),
            'type': 'binary',
            'datas': xls_file,

        }
        attachment_id = self.env['ir.attachment'].create(att_vals)
        self.env.cr.commit()
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment_id.id, ),
            'target': 'self',
        }

        return action
