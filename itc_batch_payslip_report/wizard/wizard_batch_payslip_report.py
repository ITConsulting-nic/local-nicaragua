# -*- coding: utf-8 -*-
import xlsxwriter
import base64
from odoo import fields, models, api, _
import base64
import logging
_logger = logging.getLogger(__name__)

class wizard_batch_payslip_report(models.TransientModel):
    _name = 'wizard.batch.payslip.report'
    _description = 'Wizard Batch Payslip Report'

    xls_file = fields.Binary(string='Download')
    name = fields.Char(string='File name', size=64)
    state = fields.Selection([('choose', 'choose'),
                              ('download', 'download')], default="choose", string="Status")
    batch_id = fields.Many2one('hr.payslip.run', string="Batch Ref.",
                               default=lambda self: self._context.get('active_id'))

    def get_rules_ids(self,salary_rule_ids):
        codes = []
        ids = []
        for rule in salary_rule_ids:
            instance=self.env['hr.salary.rule'].browse(int(rule))
            if instance.code not in codes:
                codes.append(instance.code)
                ids.append(instance.id)

        return self.env['hr.salary.rule'].browse(set(ids))

    def print_report_xls(self):
        batch_id = self.batch_id
        xls_filename = 'Reporte detallado de Lote de Nómina.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + xls_filename)
        worksheet = workbook.add_worksheet("Detalle de Nómina")

        text_center = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
        text_center.set_text_wrap()
        font_bold_center = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        font_bold_right = workbook.add_format({'bold': True})
        font_bold_right.set_num_format('###0.00')
        number_format = workbook.add_format()
        number_format.set_num_format('###0.00')

        worksheet.set_column('A:AZ', 18)
        for i in range(3):
            worksheet.set_row(i, 18)
        worksheet.write(0, 1, 'Compañia', font_bold_center)
        worksheet.merge_range(0, 2, 0, 3, self.env.user.company_id.name or '', text_center)
        worksheet.write(1, 1, 'Nombre', font_bold_center)
        worksheet.merge_range(1, 2, 1, 3, batch_id.name or '', text_center)
        worksheet.write(2, 1, 'Periodo', font_bold_center)
        worksheet.merge_range(2, 2, 2, 3, str(batch_id.date_start) + ' - ' + str(batch_id.date_end), text_center)
        row = 5
        worksheet.merge_range(row, 0, row + 1, 0, 'No #', font_bold_center)
        worksheet.merge_range(row, 1, row + 1, 1, 'Código', font_bold_center)
        worksheet.merge_range(row, 2, row + 1, 2, 'No. INSS', font_bold_center)
        worksheet.merge_range(row, 3, row + 1, 3, 'No. Cédula', font_bold_center)
        worksheet.merge_range(row, 4, row + 1, 4, 'Referencia', font_bold_center)
        worksheet.merge_range(row, 5, row + 1, 5, 'Empleado', font_bold_center)
        #worksheet.merge_range(row, 6, row + 1, 6, 'Nómina', font_bold_center)
        #worksheet.merge_range(row, 7, row + 1, 7, 'Linea de Negocio', font_bold_center)
        worksheet.merge_range(row, 6, row + 1, 6, 'Departamento', font_bold_center)
        worksheet.merge_range(row, 7, row + 1, 7, 'Puesto de Trabajo', font_bold_center)
        #worksheet.merge_range(row, 10, row + 1, 10, 'Jefe', font_bold_center)
        #worksheet.merge_range(row, 11, row + 1, 11, 'Objetivo', font_bold_center)
        #worksheet.merge_range(row, 12, row + 1, 12, 'Subobjetivo', font_bold_center)
        #worksheet.merge_range(row, 13, row + 1, 13, 'Jornada', font_bold_center)
        #worksheet.merge_range(row, 14, row + 1, 14, 'Estructura', font_bold_center)

        col = 8
        worksheet.set_row(row + 1, 30)
        result = self.get_header(batch_id)
        col_lst = []
        # make the header by category
        for item in result:
            for categ_id, salary_rule_ids in item.items():
                if not salary_rule_ids:
                    continue
                salary_rule_reformat=self.get_rules_ids(salary_rule_ids)
                if len(salary_rule_reformat) == 1:
                    worksheet.write(row, col, categ_id.name, font_bold_center)
                    worksheet.write(row + 1, col, salary_rule_reformat[0].name, text_center)
                    col += 1
                    col_lst.append(salary_rule_reformat[0])
                else:
                    rule_count = len(salary_rule_reformat) - 1
                    worksheet.merge_range(row, col, row, col + rule_count, categ_id.name, font_bold_center)
                    for rule_id in salary_rule_reformat.sorted(key=lambda l: l.sequence):
                        worksheet.write(row + 1, col, rule_id.name, text_center)
                        col += 1
                        col_lst.append(rule_id)
        row += 3
        sr_no = 1
        total_rule_sum_dict = {}
        # print the data of payslip
        for payslip in batch_id.mapped('slip_ids'):
            worksheet.write(row, 0, sr_no, text_center)
            worksheet.write(row, 1, payslip.employee_id.barcode)
            worksheet.write(row, 2, payslip.employee_id.num_inss)
            worksheet.write(row, 3, payslip.employee_id.num_cedula)
            worksheet.write(row, 4, payslip.number)
            worksheet.write(row, 5, payslip.employee_id.name)
            #worksheet.write(row, 6, payslip.payslip_run_id.name)
            #worksheet.write(row, 7, payslip.contract_id.lnegocio.name or '')
            worksheet.write(row, 6, payslip.employee_id.department_id.name or '')
            worksheet.write(row, 7, payslip.employee_id.job_id.name or '')
            #worksheet.write(row, 10, payslip.employee_id.parent_id.name or '')
            #worksheet.write(row, 11, payslip.contract_id.objetivo.name or '')
            #worksheet.write(row, 12, payslip.contract_id.subobjetivo.name or '')
            #worksheet.write(row, 13, payslip.contract_id.resource_calendar_id.name or '')
            #worksheet.write(row, 14, payslip.struct_id.name or '')
            col = 8
            for col_rule_id in col_lst:
                line_id = payslip.line_ids.filtered(lambda l: l.salary_rule_id.code == col_rule_id.code)
                amount = line_id.total or 0.0
                worksheet.write(row, col, amount, number_format)
                col += 1
                total_rule_sum_dict.setdefault(col_rule_id, [])
                total_rule_sum_dict[col_rule_id].append(amount)
            row += 1
            sr_no += 1
        # print the footer
        col = 8
        row += 1
        worksheet.write(row, 3, "Total", font_bold_center)
        for col_rule_id in col_lst:
            worksheet.write(row, col, sum(total_rule_sum_dict.get(col_rule_id)), font_bold_right)
            col += 1
        workbook.close()
        action = self.env.ref('itc_batch_payslip_report.action_wizard_batch_payslip_report').read()[0]
        action['res_id'] = self.id
        self.write({'state': 'download',
                    'name': xls_filename,
                    'xls_file': base64.b64encode(open('/tmp/' + xls_filename, 'rb').read())})
        return action


    def print_report_pdf(self):
        data = self.read()[0]
        return self.env.ref('itc_batch_payslip_report.action_print_batch_payslip').report_action([], data=data)


    def get_header(self, batch_id):
        category_list_ids = self.env['hr.salary.rule.category'].search([])
        # find all the rule by category
        col_by_category = {}
        for payslip in batch_id.slip_ids:
            for line in payslip.line_ids:
                col_by_category.setdefault(line.category_id, [])
                col_by_category[line.category_id] += line.salary_rule_id.ids
        for categ_id, rule_ids in col_by_category.items():
            col_by_category[categ_id] = self.env['hr.salary.rule'].browse(set(rule_ids))
        # make the category wise rule
        result = []
        for categ_id in category_list_ids:
            rule_ids = col_by_category.get(categ_id)
            if not rule_ids:
                continue
            result.append({categ_id: rule_ids.sorted(lambda l: l.sequence)})
        return result


    def action_go_back(self):
        action = self.env.ref('itc_batch_payslip_report.action_wizard_batch_payslip_report').read()[0]
        action['res_id'] = self.id
        self.write({'state': 'choose'})
        return action


class eq_batch_payslip_report_report_batch_payslip_template(models.AbstractModel):
    _name = 'report.itc_batch_payslip_report.report_batch_payslip_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'itc_batch_payslip_report.report_batch_payslip_template')
        wizard_id = self.env['wizard.batch.payslip.report'].browse(data.get('id'))
        batch_id = wizard_id.batch_id
        get_header = wizard_id.get_header(batch_id)
        get_rule_list = []
        for header_dict in get_header:
            for rule_ids in header_dict.values():
                for rule_id in rule_ids:
                    get_rule_list.append(rule_id)
        return {
            'doc_ids': self.ids,
            'doc_model': report,
            'docs': batch_id,
            'data': data,
            'batch_id': batch_id,
            '_get_header': get_header,
            '_get_rule_list': get_rule_list
        }
