# -*- coding: utf-8 -*-
{
    'name': "Reporte de retención en la fuente para la nómina",

    'summary': """
        Reporte de Planilla de retención en la fuente para la nómina
        """,

    'description': """
        Reporte de Planilla de retención en la fuente para la nómina
    """,

    'author': "ITConsulting",
    'website': "https://www.itc.services",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Payroll',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll','l10n_ni_hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/planilla_retencion.xml',
    ],
}
