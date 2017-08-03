# -*- coding: utf-8 -*-
from odoo import http

# class EtsiHrms(http.Controller):
#     @http.route('/etsi_hrms/etsi_hrms/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etsi_hrms/etsi_hrms/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('etsi_hrms.listing', {
#             'root': '/etsi_hrms/etsi_hrms',
#             'objects': http.request.env['etsi_hrms.etsi_hrms'].search([]),
#         })

#     @http.route('/etsi_hrms/etsi_hrms/objects/<model("etsi_hrms.etsi_hrms"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etsi_hrms.object', {
#             'object': obj
#         })