# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
_logger = logging.getLogger(__name__)

class IconSettings(http.Controller):
    '''for setting icon on map'''
    @http.route('/objects', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def icon_settings(self):
        ''' get icon settings'''
        dataset = http.request.env['icon_settings'].sudo().search([])
        result = []
        for data in dataset:
            result.append({
                    'name':data.name,'local':[data.local_x,data.local_y],'icon_url':data.icon_url})
        results = json.dumps({'data':result})
        return results

    @http.route('/vote_data/<string:vote_type>'
                , type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_vote_type(self,vote_type):
        ''' get vote data by vote type'''
        dataset = http.request.env['vote_data'].sudo().search([('vote_type','=',vote_type)])
        citys = []
        for i in dataset:
            citys.append(i.city)
        results = json.dumps({'data':citys})
        return results

    @http.route('/vote_data/<string:vote_type>/<string:city>'
                , type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_city(self,vote_type,city):
        ''' get vote data by vote city'''
        dataset = http.request.env['vote_data'].sudo().search(
            [('vote_type','=',vote_type)
            ,('city','=',city)])
        places = []
        for i in dataset:
            places.append(i.place)
        results = json.dumps({'data':places})
        return results

    @http.route('/vote_data/<string:vote_type>/<string:city>/<string:place>',
                 type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_get_place(self,vote_type,city,place):
        ''' get vote data by vote place'''
        dataset = http.request.env['vote_data'].sudo().search(
            [('vote_type','=',vote_type)
            ,('city','=',city)
            ,('place','=',place)])
        districts = []
        for i in dataset:
            districts.append(i.district)
        results = json.dumps({'data':districts})
        return results

    @http.route('/vote_data/<string:vote_type>/<string:city>/<string:place>/<string:district>',
                 type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def vote_data_get_district(self,vote_type,city,place,district):
        ''' get vote data by vote district'''
        dataset = http.request.env['vote_data'].sudo().search(
            [('vote_type','=',vote_type)
            ,('city','=',city)
            ,('place','=',place)
            ,('district','like',district)])
        str_results = json.dumps(dataset.data)
        results = json.loads(str_results)
        return results
    #
    @http.route('/map_data/<string:city>', type="http", auth="public",
                 methods=["GET"], csrf=False, cors='*')
    def map_data_city(self,city):
        ''' get map data by city'''
        districts = []
        dataset = http.request.env['map_data'].sudo().search([('city','=',city)])
        for i in dataset:
            districts.append(i.district)
        results = json.dumps({'data':districts})
        return results

    @http.route('/map_data/<string:city>/<string:district>', type="http",
                 auth="public", methods=["GET"], csrf=False, cors='*')
    def map_data_district(self,city,district):
        ''' get map data by district'''
        dataset = http.request.env['map_data'].sudo().search(
                [('city','=',city),('district','=',district)])
        str_results = json.dumps(dataset.data)
        results = json.loads(str_results)
        return results
