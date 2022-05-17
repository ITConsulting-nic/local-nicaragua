# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date

#DATOS ADICIONALES EN A FICHA DEL EMPLEADO
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    num_cedula = fields.Char("Número de cédula")
    num_inss = fields.Char("Número INSS")
    primer_nombre = fields.Char("Primer Nombre")
    segundo_nombre = fields.Char("Segundo Nombre")
    primer_apellido = fields.Char("Primer Apellido")
    segundo_apellido = fields.Char("Segundo Apellido")

#DATOS ADICIONALES EN EL CONTRATO DE EMPLEADOS
class HrContract(models.Model):
    _inherit = 'hr.contract'

    ctrabajo = fields.Many2one('employee.centro.inss', "Centro de trabajo (INSS)")
    saldo_ingreso_bruto = fields.Monetary("Saldo de Salario Bruto acumulado a la fecha")
    saldo_ir = fields.Monetary("Saldo de IR de Salarios a la fecha")
    saldo_ir_fecha = fields.Date("Fecha de Corte Saldos")
    saldo_ir_no_quincenas = fields.Integer("No. de Quincenas pagadas")
    pension_alimenticia = fields.Integer("Pensión alimenticia (% mensual)")
    pagar_antiguedad = fields.Boolean ("Pagar antigüedad")
    nominas_pagadas = fields.Integer(compute = '_contar_nominas_pagadas', string='Nóminas Pagadas')

    @api.depends('employee_id')
    def _contar_nominas_pagadas(self):
        hoy = date.today()
        anio_desde = "'" + str(hoy.year) + "-01-01" + "'"

        for record in self:
            record.nominas_pagadas = len([payslip for payslip in record.employee_id.slip_ids if payslip.state == 'done'and str(payslip.date_to) > anio_desde])

#DE AQUÍ EN ADELANTE CREAMOS TODAS LAS CLASES QUE NECESITEMOS
class CentroINSS(models.Model):
    _name = 'employee.centro.inss'
    _rec_name = 'name'
    _order = 'name asc'

    name = fields.Char("Nombre", required=True, translate=True)
    description = fields.Text("Descripción", translate=True)
