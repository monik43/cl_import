# -*- coding: utf-8 -*-
from odoo import http

# class ClImport(http.Controller):
#     @http.route('/cl_import/cl_import/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cl_import/cl_import/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cl_import.listing', {
#             'root': '/cl_import/cl_import',
#             'objects': http.request.env['cl_import.cl_import'].search([]),
#         })

#     @http.route('/cl_import/cl_import/objects/<model("cl_import.cl_import"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cl_import.object', {
#             'object': obj
#         })