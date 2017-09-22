# -*- coding: utf-8 -*-
from odoo import http

# class EtsiWebservice(http.Controller):
#     @http.route('/etsi_webservice/etsi_webservice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etsi_webservice/etsi_webservice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('etsi_webservice.listing', {
#             'root': '/etsi_webservice/etsi_webservice',
#             'objects': http.request.env['etsi_webservice.etsi_webservice'].search([]),
#         })

#     @http.route('/etsi_webservice/etsi_webservice/objects/<model("etsi_webservice.etsi_webservice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etsi_webservice.object', {
#             'object': obj
#         })