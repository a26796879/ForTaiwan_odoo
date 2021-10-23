# -*- coding: utf-8 -*-
# from odoo import http


# class Line-notify(http.Controller):
#     @http.route('/line-notify/line-notify/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/line-notify/line-notify/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('line-notify.listing', {
#             'root': '/line-notify/line-notify',
#             'objects': http.request.env['line-notify.line-notify'].search([]),
#         })

#     @http.route('/line-notify/line-notify/objects/<model("line-notify.line-notify"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('line-notify.object', {
#             'object': obj
#         })
