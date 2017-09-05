# -*- coding: utf-8 -*-
from odoo import http

# class EtsiExpense(http.Controller):
#     @http.route('/etsi_expense/etsi_expense/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etsi_expense/etsi_expense/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('etsi_expense.listing', {
#             'root': '/etsi_expense/etsi_expense',
#             'objects': http.request.env['etsi_expense.etsi_expense'].search([]),
#         })

#     @http.route('/etsi_expense/etsi_expense/objects/<model("etsi_expense.etsi_expense"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etsi_expense.object', {
#             'object': obj
#         })