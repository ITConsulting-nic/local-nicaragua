# -*- coding: utf-8 -*-
{
    'name': "Reporte detallado de Lote de Nómina",
    'category': 'Payroll',
    'version': '1.0',
    'author': 'ITConsulting',
    'description': """
        This Module allows to print Payroll PDF & Excel Report.
    """,
    'summary': 'This Module allows to print Payroll PDF & Excel Report.',
    'depends': ['base', 'hr_payroll'],
    'license': 'AGPL-3',
    'website': "",
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_batch_payslip_report.xml',
        'report/report_batch_payslip_template.xml',
        'report/report.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}