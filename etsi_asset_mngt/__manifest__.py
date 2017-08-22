# -*- coding: utf-8 -*-
{
    'name': "ETSI Asset Management",

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
    'depends': ['base','hr'],
    'depends': ['base', 'hr', 'stock'],

    # always loaded
    'data': [
        'views/asset_handover_views.xml',
        'views/asset_return_views.xml',
        # 'views/asset_config_views.xml',
        # 'views/warehouse_config_views.xml',
        # 'views/asset_distribution_views.xml',
        'views/asset_model_views.xml',
        'views/asset_condition_views.xml',
        'views/asset_config_views.xml',
        # 'security/ir.model.access.csv',
        'views/asset_location_change.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}