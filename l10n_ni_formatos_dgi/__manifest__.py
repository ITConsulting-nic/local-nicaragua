# -*- coding: utf-8 -*-
{
    'name': "l10n_ni_formatos_dgi",

    'summary': """
        Emite 4 reportes que forman parte de la localización nicaragüense, los reportes son NOTA DE CRÉDITO, NOTA DE DÉBITO, FACTURA, RECIBO DE CAJA. """,

    'description': """
        Emite 4 reportes que forman parte de la localización nicaragüense, los reportes son NOTA DE CRÉDITO, NOTA DE DÉBITO, FACTURA, RECIBO DE CAJA.
    """,

    'author': "ITConsulting",
    'website': "https://www.itc.services/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'num_to_words'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/account_config_setting_view.xml',
        'reports/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
