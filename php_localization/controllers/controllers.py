# -*- coding: utf-8 -*-
from odoo import http

# class PhpLocalization(http.Controller):
#     @http.route('/php_localization/php_localization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/php_localization/php_localization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('php_localization.listing', {
#             'root': '/php_localization/php_localization',
#             'objects': http.request.env['php_localization.php_localization'].search([]),
#         })

#     @http.route('/php_localization/php_localization/objects/<model("php_localization.php_localization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('php_localization.object', {
#             'object': obj
#         })