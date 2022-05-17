# -*- coding: utf-8 -*-
{
    'name': "l10n_ni_reportes_vet",

    'summary': """
        Este módulo agrega las características contables para la localización nicaragüense.""",

    'description': """
        Este módulo agrega las características contables para la localización nicaragüense.
    """,

    'author': "ITConsulting",
    'website': "https://www.itc.services/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/report.xml',
        'reports/report_planilla_retenciones.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
