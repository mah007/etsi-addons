# -*- coding: utf-8 -*-
{
    'name': "PHP Localization",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Evanscor Technology Solutions Inc.",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '10.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mail',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/cfg_localization_views.xml',
        # 'data/res_country.xml',
        # 'data/cfg.country.region.csv',
        # 'data/cfg.region.province.csv',
        # 'data/cfg.province.city.csv',
        # 'data/cfg.city.barangay.csv',


    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}