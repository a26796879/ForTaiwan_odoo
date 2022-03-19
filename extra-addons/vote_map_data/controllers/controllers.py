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
            result.append({'name':data.name,'local':[data.local_x,data.local_y],'icon_url':data.icon_url})
        results = json.dumps({'data':result})
        return results

    @http.route('/vote_data/<string:vote_type>', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_vote_type(self,vote_type):
        dataset = http.request.env['vote_data'].sudo().search([('vote_type','=',vote_type)])
        citys = []
        for i in dataset:
            citys.append(i.city)
        results = json.dumps({'data':citys})
        return results

    @http.route('/vote_data/<string:vote_type>/<string:city>', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_city(self,vote_type,city):
        dataset = http.request.env['vote_data'].sudo().search([('vote_type','=',vote_type),('city','=',city)])
        places = []
        for i in dataset:
            places.append(i.place)
        results = json.dumps({'data':places})
        return results

    @http.route('/vote_data/<string:vote_type>/<string:city>/<string:place>', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_get_place(self,vote_type,city,place):
        dataset = http.request.env['vote_data'].sudo().search([('vote_type','=',vote_type),('city','=',city),('place','=',place)])
        districts = []
        for i in dataset:
            districts.append(i.district)
        results = json.dumps({'data':districts})
        return results
    #
    @http.route('/vote_data/<string:vote_type>/<string:city>/<string:place>/<string:district>', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_district(self,vote_type,city,place,district):
        dataset = http.request.env['vote_data'].sudo().search([('vote_type','=',vote_type),('city','=',city),('place','=',place),('district','=',district)])
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
        results = json.dumps({'data':districts})
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
