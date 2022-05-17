# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from datetime import timedelta
from math import fabs
from dateutil.relativedelta import relativedelta

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
    service_duration = fields.Integer(compute= '_compute_service_duration', string='Tiempo trabajado (total días)', readonly=True)
    service_duration_years = fields.Integer(compute= "_compute_service_duration_display", string="Tiempo trabajado (años)", readonly=True)
    service_duration_months = fields.Integer(compute="_compute_service_duration_display", string="Tiempo trabajado (meses)", readonly=True)
    service_duration_days = fields.Integer(compute="_compute_service_duration_display", string="Tiempo trabajado (días)", readonly=True)
    fecha_ultimo_aguinaldo = fields.Date("Fecha de Pago del último aguinaldo")
    aguinaldo_acumulado_days = fields.Integer(compute="_compute_service_duration_display", string="Aguinaldo acumulado (días)", readonly=True)
    aguinaldo_acumulado_months = fields.Integer(compute="_compute_service_duration_display", string="Aguinaldo acumulado (meses)", readonly=True)

    @api.depends('employee_id')
    def _contar_nominas_pagadas(self):
        hoy = date.today()
        anio_desde = "'" + str(hoy.year) + "-01-01" + "'"

        for record in self:
            record.nominas_pagadas = len([payslip for payslip in record.employee_id.slip_ids if payslip.state == 'done'and str(payslip.date_to) > anio_desde])

    @api.depends("date_start", "date_end")
    def _compute_service_duration(self):
        for record in self:
            service_until = record.date_end or fields.Date.today()
            if record.date_start and service_until > record.date_start:
                service_since = record.date_start
                service_duration = fabs(
                    (service_until - service_since) / timedelta(days=1)
                )
                record.service_duration = int(service_duration)
            else:
                record.service_duration = 0

    @api.depends("date_start", "date_end", "fecha_ultimo_aguinaldo")
    def _compute_service_duration_display(self):
        for record in self:
            service_until = record.date_end or fields.Date.today()
            if record.date_start and service_until > record.date_start:
                service_duration = relativedelta(
                    service_until, record.date_start
                )
                record.service_duration_years = service_duration.years
                record.service_duration_months = service_duration.months
                record.service_duration_days = service_duration.days
            else:
                record.service_duration_years = 0
                record.service_duration_months = 0
                record.service_duration_days = 0

            #PARA CALCULAR EL AGUINALDO
            if record.fecha_ultimo_aguinaldo and service_until > record.fecha_ultimo_aguinaldo:
                aguinaldo_days = relativedelta(service_until, record.fecha_ultimo_aguinaldo)
                record.aguinaldo_acumulado_days = aguinaldo_days.days
                record.aguinaldo_acumulado_months = aguinaldo_days.months
            else:
                record.aguinaldo_acumulado_days = 0
                record.aguinaldo_acumulado_months = 0

#DE AQUÍ EN ADELANTE CREAMOS TODAS LAS CLASES QUE NECESITEMOS
class CentroINSS(models.Model):
    _name = 'employee.centro.inss'
    _rec_name = 'name'
    _order = 'name asc'

    name = fields.Char("Nombre", required=True, translate=True)
    description = fields.Text("Descripción", translate=True)
