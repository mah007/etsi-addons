# -*- coding: utf-8 -*-
{
    'name': "evanscor_foodpark",

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
    'depends': ['base','website','website_sale','point_of_sale','website_sale','account_accountant','purchase','website_customer','mrp','report',
                'point_of_sale_products_date_expiration','pos_stock_avail','web_site_sale_exten',
                'website_animate','website_customer_order_delivery_date','website_multi_image_zoom','website_sale_product_quick_view',
                'website_sale_stock_status','odoo_web_login','chart_of_account_hierarchy','account_asset','l10n_generic_coa'],
# web_responsive

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/accounts_receivable_wizard_view.xml',
        'views/accounts_receivable_wizard_temp.xml',
        # 'views/custom_stock_picking_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}