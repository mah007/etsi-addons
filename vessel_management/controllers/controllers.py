# -*- coding: utf-8 -*-
from odoo import http

# class VesselManagement(http.Controller):
#     @http.route('/vessel_management/vessel_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vessel_management/vessel_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vessel_management.listing', {
#             'root': '/vessel_management/vessel_management',
#             'objects': http.request.env['vessel_management.vessel_management'].search([]),
#         })

#     @http.route('/vessel_management/vessel_management/objects/<model("vessel_management.vessel_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vessel_management.object', {
#             'object': obj
#         })