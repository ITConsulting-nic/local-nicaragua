# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#    Coded by: Fernando de la Nuez Granizo (fdelanuez@itc.services),
#    Jesús Rabelo Pérez (jrabelo@itc.services)
#    Finance by: ITConsulting.
#    Audited by: Daysi Alvarado (dalvarado@itc.services),
#    Bryan Oviedo (boviedo@itc.services)

{
    "name": "Nicaragua - Accounting",
    "version": "14.0",
    "author": "ITConsulting",
    'category': 'Accounting/Localizations/Account Charts',
    "description": """
Minimal accounting configuration for Nicaragua.
===============================================

This Chart of account is a minimal proposal to be able to use the accounting
feature of Odoo.

This doesn't pretend be all the localization for Nicaragua it is just the
minimal data required to start from 0 in nicaraguan localization.

With this module you will have:

 - Minimal chart of account tested in production environments.
 - Minimal chart of taxes, to comply with DGI requirements.
    """,
    "depends": [
        "account",
    ],
    "data": [
        'data/account_chart_template_data.xml',
        'data/account.account.template.csv',
        'data/account_chart_template_post_data.xml',
        'data/account_tax_report_data.xml',
        'data/account_tax_template_group.xml',
        'data/account_tax_template_data.xml',
        'data/account_chart_template_configure_data.xml',
        'data/account.group.template.csv',
    ],
}
