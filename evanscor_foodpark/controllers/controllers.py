# -*- coding: utf-8 -*-
from odoo import http

# class EvanscorFoodpark(http.Controller):
#     @http.route('/evanscor_foodpark/evanscor_foodpark/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/evanscor_foodpark/evanscor_foodpark/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('evanscor_foodpark.listing', {
#             'root': '/evanscor_foodpark/evanscor_foodpark',
#             'objects': http.request.env['evanscor_foodpark.evanscor_foodpark'].search([]),
#         })

#     @http.route('/evanscor_foodpark/evanscor_foodpark/objects/<model("evanscor_foodpark.evanscor_foodpark"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('evanscor_foodpark.object', {
#             'object': obj
#         })