# -*- coding: utf-8 -*-
from odoo import http
import json, logging
_logger = logging.getLogger(__name__)

class Icon_Settings(http.Controller):
    @http.route('/objects', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def icon_settings(self):
        dataset = http.request.env['icon_settings'].sudo().search([])
        result = []
        for data in dataset:
            _logger.debug(data.name)
            result.append({'name':data.name,'local':[data.local_x,data.local_y],'icon_url':data.icon_url})
        results = json.dumps({'data':result})
        return results

    @http.route('/vote_data', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data(self):
        dataset = http.request.env['vote_data'].sudo().search([('city','=','高雄市'),('district','=','三民區')])
        str_results = json.dumps(dataset.data)
        results = json.loads(str_results)
        return results

    @http.route('/map_data', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def map_data(self):
        dataset = http.request.env['map_data'].sudo().search([('city','=','高雄市'),('district','=','三民區')])
        str_results = json.dumps(dataset.data)
        results = json.loads(str_results)
        return results


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
