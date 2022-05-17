import base64
import logging
import tempfile
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging as _logger
try:
    import xlsxwriter
except ImportError:
    _logger.warning("Cannot import xlsxwriter")
    xlsxwriter = False


class PlanillaCreditoIVA(models.TransientModel):
    _name = "planilla.credito.iva"

    date_init = fields.Date("Fecha de inicio",required=True)
    date_end = fields.Date("Fecha de finalización",required=True)


    def generate_xls(self):
        if not xlsxwriter:
            raise UserError(_("The Python library xlsxwriter is installed. Contact your system administrator"))

        if self.date_init >= self.date_end:
            raise UserError(_("La fecha de inicio no puede ser mayor o igual a la fecha de finalización"))
        else:
            domain = [('invoice_date', '<=', self.date_end),('invoice_date','>=',self.date_init)]
            moves=self.env['account.move'].search(domain)
            if not moves:
                raise UserError(_("No se encontro ningún registro coincidente para el rango de fechas seleccionado"))
            else:
                file_path = tempfile.mktemp(suffix='.xlsx')
                workbook = xlsxwriter.Workbook(file_path)
                styles = {
                    'main_data': workbook.add_format({
                        'font_size': 10,
                        'border': 1,
                        'bold': False,
                    }),
                    'main_data_bold': workbook.add_format({
                        'font_size': 10,
                        'border': 1,
                        'bold': True,
                    }),

                }
                worksheet = workbook.add_worksheet("Reporte Planilla Crédito IVA")
                worksheet.set_column(0, 0, 15)
                worksheet.set_column(1, 1, 35)
                worksheet.set_column(2, 2, 20)
                worksheet.set_column(3, 3, 20)
                worksheet.set_column(4, 4, 17)
                worksheet.set_column(5, 5, 15)
                worksheet.set_column(6, 6, 20)
                worksheet.set_column(7, 7, 15)
                

                worksheet.write(0,0, "No. RUC", styles.get("main_data_bold"))
                worksheet.write(0,1, "Nombre y Apellidos o Razón Social", styles.get("main_data_bold"))
                worksheet.write(0,2, "No. Documento", styles.get("main_data_bold"))
                worksheet.write(0,3, "Descripción del Pago", styles.get("main_data_bold"))
                worksheet.write(0,4, "Fecha de Documento", styles.get("main_data_bold"))
                worksheet.write(0,5, "Ingresos sin IVA", styles.get("main_data_bold"))
                worksheet.write(0,6, "Monto IVA Trasladado", styles.get("main_data_bold"))
                worksheet.write(0,7, "No. del Renglón", styles.get("main_data_bold"))

                col = 0
                for m in moves:
                    col+=1
                    worksheet.write(col,0, m.partner_id.vat or "N/A", styles.get("main_data"))
                    worksheet.write(col,1, m.partner_id.name or "N/A", styles.get("main_data"))
                    worksheet.write(col,2, m.name or "N/A", styles.get("main_data"))
                    worksheet.write(col,3, "N/A", styles.get("main_data"))
                    worksheet.write(col,4, str(m.invoice_date) or "N/A", styles.get("main_data"))
                    worksheet.write(col,5, m.amount_untaxed or "N/A", styles.get("main_data"))
                    worksheet.write(col,6, "N/A", styles.get("main_data"))
                    worksheet.write(col,7, "N/A", styles.get("main_data"))



                
                workbook.close()
                with open(file_path, 'rb') as r:
                    xls_file = base64.b64encode(r.read())
                att_vals = {
                    'name': u"{}#{}.xlsx".format("Reporte Planilla Crédito IVA", fields.Date.today()),
                    'type': 'binary',
                    'datas': xls_file,
                }
                attachment_id = self.env['ir.attachment'].create(att_vals)
                self.env.cr.commit()
                action = {
                    'type': 'ir.actions.act_url',
                    'url': '/web/content/{}?download=true'.format(attachment_id.id, ),
                    'target': 'reload',
                }

                return action

        return
