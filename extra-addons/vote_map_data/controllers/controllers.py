# -*- coding: utf-8 -*-
from odoo import http,logging

_logger = logging.getLogger(__name__)

class Icon_Settings(http.Controller):
    @http.route('/objects', type="http", auth="public", methods=["GET"], csrf=False)
    def index(self):
        result = http.request.env['vote_map_data.icon_settings'].search([])
        _logger.debug(result)
        return 'test'

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
