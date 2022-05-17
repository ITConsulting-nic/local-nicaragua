# -*- coding: utf-8 -*-
{
    'name': "Reporte SIE INSS",

    'summary': """
        Reporte de Planilla para el SIE INSS
        """,

    'description': """
        Reporte de Planilla para el SIE INSS
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
        'wizard/sie_inss.xml',
    ],
}
