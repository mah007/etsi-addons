# -*- coding: utf-8 -*-
from odoo import http

# class EtsiPayroll(http.Controller):
#     @http.route('/etsi_payroll/etsi_payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etsi_payroll/etsi_payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('etsi_payroll.listing', {
#             'root': '/etsi_payroll/etsi_payroll',
#             'objects': http.request.env['etsi_payroll.etsi_payroll'].search([]),
#         })

#     @http.route('/etsi_payroll/etsi_payroll/objects/<model("etsi_payroll.etsi_payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etsi_payroll.object', {
#             'object': obj
#         })