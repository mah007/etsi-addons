# -*- coding: utf-8 -*-
from odoo import http

# class EtsiSale(http.Controller):
#     @http.route('/etsi_sale/etsi_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etsi_sale/etsi_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('etsi_sale.listing', {
#             'root': '/etsi_sale/etsi_sale',
#             'objects': http.request.env['etsi_sale.etsi_sale'].search([]),
#         })

#     @http.route('/etsi_sale/etsi_sale/objects/<model("etsi_sale.etsi_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etsi_sale.object', {
#             'object': obj
#         })