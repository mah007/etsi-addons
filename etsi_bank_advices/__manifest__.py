# -*- coding: utf-8 -*-
{
    'name': "ETSI-Bank Advice",

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
    'depends': ['base', 'mail', 'contacts', 'report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'template/report/bank_advice_report_template.xml',
        'views/hr_bank_advice_views.xml',
        'template/bank_advice_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}