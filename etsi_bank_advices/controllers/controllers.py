# -*- coding: utf-8 -*-
from odoo import http

# class EtsiBankAdvices(http.Controller):
#     @http.route('/etsi_bank_advices/etsi_bank_advices/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etsi_bank_advices/etsi_bank_advices/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('etsi_bank_advices.listing', {
#             'root': '/etsi_bank_advices/etsi_bank_advices',
#             'objects': http.request.env['etsi_bank_advices.etsi_bank_advices'].search([]),
#         })

#     @http.route('/etsi_bank_advices/etsi_bank_advices/objects/<model("etsi_bank_advices.etsi_bank_advices"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etsi_bank_advices.object', {
#             'object': obj
#         })