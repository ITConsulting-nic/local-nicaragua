from odoo import api, models, fields
from datetime import date
from datetime import timedelta
from math import fabs
from dateutil.relativedelta import relativedelta

class Payslip(models.Model):
    _inherit = 'hr.payslip'

    aguinaldo_acumulado_days = fields.Integer(compute="_compute_service_duration_display", string="Aguinaldo acumulado (días)", readonly=True)
    aguinaldo_acumulado_months = fields.Integer(compute="_compute_service_duration_display", string="Aguinaldo acumulado (meses)", readonly=True)

    #Esta función nos permite acceder a las diferentes funciones necesarias para
    #los calculos especiales requeridos por la localización Nicaragua.
    def _get_base_local_dict(self):
        res = super()._get_base_local_dict()
        res.update({
        'compute_ir': compute_ir,
        'compute_ir_inge': compute_ir_inge,
        'compute_aguinaldo': compute_aguinaldo,
        })
        return res

    @api.depends("contract_id", "date_from", "date_to")
    def _compute_service_duration_display(self):
        for record in self:
            service_until = record.date_to or fields.Date.today()

            #PARA CALCULAR EL AGUINALDO
            if record.date_to and service_until > record.date_from:
                aguinaldo_days = relativedelta(service_until, record.date_from)
                record.aguinaldo_acumulado_days = aguinaldo_days.days
                record.aguinaldo_acumulado_months = aguinaldo_days.months
            else:
                record.aguinaldo_acumulado_days = 0
                record.aguinaldo_acumulado_months = 0

#CALCULO DE IR LABORAL PARA LOS SIGUIENTES ESCENARIOS
# 1. Periodo Completo (Art. 19.1 RL822) e Incompleto (Art. 19.4 RL822)
# 2. Salario Variable (art. 19.6 RL822)
def compute_ir(payslip, categories, salario_acumulado, meses_transcurridos, ir_acumulado_anio, ir_acumulado_mes):

    #PASOS
    #1 DETERMINO EL SALARIO PROMEDIO MENSUAL
    salario_promedio_mensual = salario_acumulado / meses_transcurridos

    #2 DETERMINO LA EXPECTATVIA ANUAL POR SALARIOS
    expectativa_anual_x_salarios = salario_promedio_mensual * 12

    #3 DETERMINO EL IR ANUAL
    renta_anual_salarios = compute_renta_anual(expectativa_anual_x_salarios)

    #4 DETERMINO EL IR COEFICIENTE MENSUAL
    ir_coeficiente_mensual = renta_anual_salarios / 12
    ir_salarios = ir_coeficiente_mensual * meses_transcurridos

    #5 DETERMINO EL IR DEL MES POR SALARIOS
    ir_acumulado = ir_acumulado_anio - ir_acumulado_mes
    if (ir_salarios - ir_acumulado) > 0:
        ir_mensual_salarios = ir_salarios - ir_acumulado
    else:
        ir_mensual_salarios = 0

    ir_mensual = ir_mensual_salarios

    res = ir_mensual

    return res
#CALCULO DE IR LABORAL PARA LOS SIGUIENTES ESCENARIOS
# 1. Pagos Ocasionales (Art. 19.2 del RL822)
def compute_ir_inge(payslip, categories, salario_acumulado, meses_transcurridos, ingresos_ocasionales):

    #PASOS
    #1 CALCULO EL IR ANUAL POR SALARIOS
    #1.1 DETERMINO EL SALARIO PROMEDIO MENSUAL
    salario_promedio_mensual = salario_acumulado / meses_transcurridos

    #1.2 DETERMINO LA EXPECTATVIA ANUAL POR SALARIOS
    expectativa_anual_x_salarios = salario_promedio_mensual * 12

    #1.3 DETERMINO EL IR ANUAL
    renta_anual_salarios = compute_renta_anual(expectativa_anual_x_salarios)

    #2 DETERMINO LA EXPECTATVIA ANUAL POR INGRESOS OCASIONALES
    expectativa_anual_x_ingresos_ocasionales = expectativa_anual_x_salarios + ingresos_ocasionales

    #4 DETERMINO EL IR ANUAL INCLUYENDO INGRESOS OCASIONALES
    renta_anual_ingresos_ocasionales = compute_renta_anual(expectativa_anual_x_ingresos_ocasionales)

    #5 DETERMINO EL IR DEL MES POR INGRESOS OCASIONALES
    ir_ingresos_ocasionales = renta_anual_ingresos_ocasionales - renta_anual_salarios

    if ir_ingresos_ocasionales > 0: res = ir_ingresos_ocasionales
    else: res = 0

    return res

#CALCULO DE IR SEGÚN TABLA PROGRESIVA
def compute_renta_anual(expectativa_anual):

    if expectativa_anual>=0.00 and expectativa_anual<=100000.00:
    	impuesto_base=0.00
    	porcentaje_aplicable=0.00
    	sobre_exceso_de=0.00
    elif expectativa_anual>100000.00 and expectativa_anual<=200000.00:
    	impuesto_base=0.00
    	porcentaje_aplicable=0.15
    	sobre_exceso_de=100000.00
    elif expectativa_anual>200000.00 and expectativa_anual<=350000.00:
    	impuesto_base=15000.00
    	porcentaje_aplicable=0.20
    	sobre_exceso_de=200000.00
    elif expectativa_anual>350000.00 and expectativa_anual<=500000.00:
    	impuesto_base=45000.00
    	porcentaje_aplicable=0.25
    	sobre_exceso_de=350000.00
    elif expectativa_anual>500000.00:
    	impuesto_base=82500.00
    	porcentaje_aplicable=0.30
    	sobre_exceso_de=500000.00

    renta_anual= impuesto_base + ((expectativa_anual - sobre_exceso_de) * porcentaje_aplicable)

    res = renta_anual

    return res

#CALCULO DEL AGUINALDO NICARAGUA
def compute_aguinaldo(num1,num2):
    #res = abs(7)
    res = num1+num2
    return res
