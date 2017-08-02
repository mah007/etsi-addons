# -*- coding: utf-8 -*-
from odoo import http

# class Git/etsi-addons/etsiBase(http.Controller):
#     @http.route('/git/etsi-addons/etsi_base/git/etsi-addons/etsi_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/git/etsi-addons/etsi_base/git/etsi-addons/etsi_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('git/etsi-addons/etsi_base.listing', {
#             'root': '/git/etsi-addons/etsi_base/git/etsi-addons/etsi_base',
#             'objects': http.request.env['git/etsi-addons/etsi_base.git/etsi-addons/etsi_base'].search([]),
#         })

#     @http.route('/git/etsi-addons/etsi_base/git/etsi-addons/etsi_base/objects/<model("git/etsi-addons/etsi_base.git/etsi-addons/etsi_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('git/etsi-addons/etsi_base.object', {
#             'object': obj
#         })