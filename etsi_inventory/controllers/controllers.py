# -*- coding: utf-8 -*-
from odoo import http

# class EtsiInventory(http.Controller):
#     @http.route('/etsi_inventory/etsi_inventory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etsi_inventory/etsi_inventory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('etsi_inventory.listing', {
#             'root': '/etsi_inventory/etsi_inventory',
#             'objects': http.request.env['etsi_inventory.etsi_inventory'].search([]),
#         })

#     @http.route('/etsi_inventory/etsi_inventory/objects/<model("etsi_inventory.etsi_inventory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etsi_inventory.object', {
#             'object': obj
#         })