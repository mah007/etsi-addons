# -*- coding: utf-8 -*-
{
    'name': "ETSI-Base",

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
    'depends': ['website','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/bank_info_views.xml',
        'views/website_templates.xml',
        'views/partner_views.xml',
        'data/ir_mail_server.xml',
        'views/partner_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}