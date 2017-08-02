# -*- coding: utf-8 -*-
from odoo import http

# class HrGovernmentIds(http.Controller):
#     @http.route('/hr_government_ids/hr_government_ids/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_government_ids/hr_government_ids/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_government_ids.listing', {
#             'root': '/hr_government_ids/hr_government_ids',
#             'objects': http.request.env['hr_government_ids.hr_government_ids'].search([]),
#         })

#     @http.route('/hr_government_ids/hr_government_ids/objects/<model("hr_government_ids.hr_government_ids"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_government_ids.object', {
#             'object': obj
#         })