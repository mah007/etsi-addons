# -*- coding: utf-8 -*-
from odoo import http

# class FoodparkUi(http.Controller):
#     @http.route('/foodpark__ui/foodpark__ui/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/foodpark__ui/foodpark__ui/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('foodpark__ui.listing', {
#             'root': '/foodpark__ui/foodpark__ui',
#             'objects': http.request.env['foodpark__ui.foodpark__ui'].search([]),
#         })

#     @http.route('/foodpark__ui/foodpark__ui/objects/<model("foodpark__ui.foodpark__ui"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('foodpark__ui.object', {
#             'object': obj
#         })