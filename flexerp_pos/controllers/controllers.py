# -*- coding: utf-8 -*-
from odoo import http

# class FlexerpPos(http.Controller):
#     @http.route('/flexerp_pos/flexerp_pos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/flexerp_pos/flexerp_pos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('flexerp_pos.listing', {
#             'root': '/flexerp_pos/flexerp_pos',
#             'objects': http.request.env['flexerp_pos.flexerp_pos'].search([]),
#         })

#     @http.route('/flexerp_pos/flexerp_pos/objects/<model("flexerp_pos.flexerp_pos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('flexerp_pos.object', {
#             'object': obj
#         })