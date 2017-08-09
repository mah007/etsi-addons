# -*- coding: utf-8 -*-
{
    'name': "ETSI-Payroll",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "ETSI",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll', 'etsi_hrms','hr_payroll_timesheet', 'payroll_period','send_email_payslips'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/hr_payroll_config_view.xml',
        'views/hr_payroll_view.xml',
        'views/partner_views.xml',
        # 'views/payroll_advance_salary_views.xml',
        'views/hr_attendance_view.xml',
        'views/hr_payroll_register_views.xml',
        # 'views/hr_payroll_report_views.xml',
        'views/report_contributionregister_templates.xml',
        'views/hr_annual_tax_views.xml',
        'views/report_payslip_templates.xml',
        'views/report_payroll_register.xml',
        'views/report_annual_tax_templates.xml',
        'data/payroll.sss.matrix.csv',
        'data/payroll.philhealth.matrix.csv',
        'data/payroll.pagibig.matrix.csv',
        'data/payroll.tax.period.csv',
        'data/payroll.tax.status.csv',
        'data/payroll.tax.exemption.csv',
        'data/payroll.tax.income.range.csv',
        # 'data/payroll.ot.day.type.xml',
        'data/payroll.contribution.register.xml',
        'data/payroll.salary.rule.xml',
        # 'data/res.partner.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}