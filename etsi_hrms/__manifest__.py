# -*- coding: utf-8 -*-
{
    'name': "ETSI-Hrms",

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
    'depends': [
        'php_localization',
        'sale',
        # 'etsi_base',
        'hr_family',
        'hr_experience',
        'hr_holidays',
        'hr_emergency_contact',
        'hr_contract',
        'website_hr_recruitment',
        'hr_recruitment_survey',
        'hr_timesheet_attendance',
        'hr_employee_time_clock',
        'hr_public_holidays',
        'timesheets_by_employee',
    ],

    # always loaded
    'data': [
        # 'security/groups.xml',
        'security/ir.model.access.csv',
        'data/employee_category.xml',
        'data/hr_contract.xml',
        'data/resource_calendar.xml',
        'data/hr_recruitment.xml',
        'data/hr_overtime.xml',
        'data/policy.xml',
        'views/resource_views.xml',
        'views/company_views.xml',
        'views/hr_views.xml',
        'views/hr_attendance_login_views.xml',
        'views/hr_holidays_views.xml',
        'views/hr_overtime_views.xml',
        'views/partner_view.xml',
        'views/contract_views.xml',
        'views/hr_recruitment_views.xml',
        'views/hr_recruitment_job_offer_views.xml',
        'views/templates.xml',
        'views/hr_policy_group_views.xml',
        'views/hr_policy_absence_views.xml',
        'views/hr_policy_overtime_views.xml',
        'reports/templates/job_offer_temp.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': True,
}