# -*- coding: utf-8 -*-
{
    'name': "Nicaraguan-Payroll",
    'description': """
    Nicaraguan Payroll Rules.

    """,

    'author': "ITConsulting",
    'website': "https://www.itc.services",
    'category': 'Payroll Localization',
    'version': '1.0',
    'depends': ['hr_payroll','hr_contract_reports','base','hr','hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/resource.calendar.csv',
        'data/account.journal.csv',
        'data/hr.work.entry.type.csv',
        'data/hr.leave.type.csv',
        'data/hr.salary.rule.category.csv',
        'data/hr.payroll.structure.type.csv',
        'data/hr.payroll.structure.csv',
        'data/after/hr.payroll.structure.type.csv',
        'data/hr.salary.rule.csv',
        'data/hr.payslip.input.type.csv',
    ],
    'auto_install': False,
}
