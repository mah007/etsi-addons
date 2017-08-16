# -*- coding: utf-8 -*-
from odoo import http

# class EtsiAssetMngt(http.Controller):
#     @http.route('/etsi_asset_mngt/etsi_asset_mngt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etsi_asset_mngt/etsi_asset_mngt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('etsi_asset_mngt.listing', {
#             'root': '/etsi_asset_mngt/etsi_asset_mngt',
#             'objects': http.request.env['etsi_asset_mngt.etsi_asset_mngt'].search([]),
#         })

#     @http.route('/etsi_asset_mngt/etsi_asset_mngt/objects/<model("etsi_asset_mngt.etsi_asset_mngt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etsi_asset_mngt.object', {
#             'object': obj
#         })