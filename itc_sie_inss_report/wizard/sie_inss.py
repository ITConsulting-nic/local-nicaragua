# -*- coding: utf-8 -*-

import base64
import logging
import tempfile
from odoo import models, exceptions, fields, api, _
import logging as _logger
import csv



class fichamaestra(models.TransientModel):
    _name = "itc.sie_inss.report"

    def find_rule_value(self, list, code):
        sol = 0
        for lines in list:
            if lines.code == code:
                sol = lines.total
                break
        return sol

    def print_csv_report(self):
        payslips = self.env.context.get('active_ids')

        file_path = tempfile.mktemp(suffix='.csv')
        with open(file_path, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(
                ['INSS', 'PRIMER_NOMBRE', 'PRIMER_APELLIDO', 'NOMINA', 'TIPO_DE_NOVEDAD', 'FECHA_DE_NOVEDAD',
                 'SALARIO_DEVENGADO', 'SALARIO_MENSUAL', 'APORTE', 'NUMERO_DE_SEMANAS_LABORADAS',
                 'CENTRO', 'EMPLEO'])
            if payslips:
                dict_employee_name = dict()
                for payslip in payslips:
                    procesamiento = self.env['hr.payslip.run'].browse(payslip)
                    if procesamiento:
                        for slip in procesamiento.slip_ids:
                            dict_slip = {'INSS': slip.employee_id.num_inss or "",
                                         'PRIMER_NOMBRE': slip.employee_id.primer_nombre or "",
                                         'PRIMER_APELLIDO': slip.employee_id.primer_apellido or "",
                                         'NOMINA': 1,
                                         'TIPO_DE_NOVEDAD': "",
                                         'FECHA_DE_NOVEDAD': "",
                                         'SALARIO_DEVENGADO': slip.contract_id.wage or 0,
                                         'SALARIO_MENSUAL': self.find_rule_value(slip.line_ids, "GROSS"),
                                         'APORTE': self.find_rule_value(slip.line_ids, "DED201"),
                                         'NUMERO_DE_SEMANAS_LABORADAS': "",
                                         'CENTRO': slip.contract_id.department_id.name or "",
                                         'EMPLEO': slip.employee_id.job_id.name or ""
                                         }
                            if slip.employee_id.name in dict_employee_name:
                                dict_employee_name[slip.employee_id.name].update(
                                    {'SALARIO_DEVENGADO': dict_employee_name[slip.employee_id.name].get("SALARIO_DEVENGADO") + dict_slip.get("SALARIO_DEVENGADO"),
                                     'SALARIO_MENSUAL': dict_employee_name[slip.employee_id.name].get("SALARIO_MENSUAL") + dict_slip.get("SALARIO_MENSUAL")
                                     })
                            else:
                                dict_employee_name[slip.employee_id.name] = dict_slip


                for name in dict_employee_name:
                    spamwriter.writerow(
                        [dict_employee_name[name].get("INSS"), dict_employee_name[name].get("PRIMER_NOMBRE"),
                         dict_employee_name[name].get("PRIMER_APELLIDO"), dict_employee_name[name].get("NOMINA"),
                         dict_employee_name[name].get("TIPO_DE_NOVEDAD"),dict_employee_name[name].get("FECHA_DE_NOVEDAD"),
                         dict_employee_name[name].get("SALARIO_DEVENGADO"),dict_employee_name[name].get("SALARIO_MENSUAL"),
                         dict_employee_name[name].get("APORTE"),dict_employee_name[name].get("NUMERO_DE_SEMANAS_LABORADAS"),
                         dict_employee_name[name].get("CENTRO"),dict_employee_name[name].get("EMPLEO")])

        with open(file_path, 'rb') as r:
            csv_file = base64.b64encode(r.read())
        att_vals = {
            'name': u"{}#{}.csv".format("Reporte SIE INSS", fields.Date.today()),
            'type': 'binary',
            'datas': csv_file,
        }
        attachment_id = self.env['ir.attachment'].create(att_vals)
        self.env.cr.commit()
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment_id.id, ),
            'target': 'self',
        }
        return action
