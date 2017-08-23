# -*- coding: utf-8 -*-
from odoo import http

# class WsiPayslipReport(http.Controller):
#     @http.route('/wsi_payslip_report/wsi_payslip_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wsi_payslip_report/wsi_payslip_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wsi_payslip_report.listing', {
#             'root': '/wsi_payslip_report/wsi_payslip_report',
#             'objects': http.request.env['wsi_payslip_report.wsi_payslip_report'].search([]),
#         })

#     @http.route('/wsi_payslip_report/wsi_payslip_report/objects/<model("wsi_payslip_report.wsi_payslip_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wsi_payslip_report.object', {
#             'object': obj
#         })