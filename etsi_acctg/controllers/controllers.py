# -*- coding: utf-8 -*-
from odoo import http

# class EtsiAcctg(http.Controller):
#     @http.route('/etsi_acctg/etsi_acctg/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etsi_acctg/etsi_acctg/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('etsi_acctg.listing', {
#             'root': '/etsi_acctg/etsi_acctg',
#             'objects': http.request.env['etsi_acctg.etsi_acctg'].search([]),
#         })

#     @http.route('/etsi_acctg/etsi_acctg/objects/<model("etsi_acctg.etsi_acctg"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etsi_acctg.object', {
#             'object': obj
#         })