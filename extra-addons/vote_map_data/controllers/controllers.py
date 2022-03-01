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

    @http.route('/vote_data/<string:vote_type>', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_vote_type(self,vote_type):
        dataset = http.request.env['vote_data'].sudo().search([('vote_type','=',vote_type)])
        citys = []
        for i in dataset:
            citys.append(i.city)
            _logger.debug(i.city)
        results = json.dumps({'data':citys})
        _logger.debug(results)
        return results

    @http.route('/vote_data/<string:vote_type>/<string:city>', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_city(self,vote_type,city):
        dataset = http.request.env['vote_data'].sudo().search([('vote_type','=',vote_type),('city','=',city)])
        vote_places = []
        for i in dataset:
            vote_places.append(i.vote_place)
            _logger.debug(i.vote_place)
        results = json.dumps({'data':vote_places})
        _logger.debug(results)
        return results

    @http.route('/vote_data/<string:vote_type>/<string:city>/<string:place>', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_place(self,vote_type,city,place):
        dataset = http.request.env['vote_data'].sudo().search([('vote_type','=',vote_type),('city','=',city),('place','=',place)])
        str_results = json.dumps(dataset.data)
        results = json.loads(str_results)
        return results
    #
    @http.route('/vote_data/<string:vote_type>/<string:city>/<string:district>', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_district(self,vote_type,city,district):
        dataset = http.request.env['vote_data'].sudo().search([('vote_type','=',vote_type),('city','=',city),('district','=',district)])
        str_results = json.dumps(dataset.data)
        results = json.loads(str_results)
        return results
    #
    @http.route('/map_data/<string:city>', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def map_data_city(self,city):
        districts = []
        dataset = http.request.env['map_data'].sudo().search([('city','=',city)])
        for i in dataset:
            districts.append(i.district)
            _logger.debug(i.district)
        results = json.dumps({'data':districts})
        _logger.debug(results)
        return results

    @http.route('/map_data/<string:city>/<string:district>', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def map_data_district(self,city,district):
        dataset = http.request.env['map_data'].sudo().search([('city','=',city),('district','=',district)])
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
