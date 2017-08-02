# -*- coding: utf-8 -*-
{
    'name': "Vessel Management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','etsi_hrms','etsi_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/employee_category.xml',
        'data/res.bank.csv',
        'data/res.bank.branch.csv',
        'data/port.embarkation.csv',
        'views/vessel_management_views.xml',
        'views/vessel_cfg_views.xml',
        'views/sea_services_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_views.xml',
        'views/templates.xml',
        'views/partner_views.xml',
        'views/sign_on_off_mngt_views.xml',
        'views/remittance_advice_views.xml',
        'views/hr_payroll_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}