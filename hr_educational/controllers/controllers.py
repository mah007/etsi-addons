# -*- coding: utf-8 -*-
from odoo import http

# class HrEducational(http.Controller):
#     @http.route('/hr_educational/hr_educational/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_educational/hr_educational/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_educational.listing', {
#             'root': '/hr_educational/hr_educational',
#             'objects': http.request.env['hr_educational.hr_educational'].search([]),
#         })

#     @http.route('/hr_educational/hr_educational/objects/<model("hr_educational.hr_educational"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_educational.object', {
#             'object': obj
#         })