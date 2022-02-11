from unittest import result
from odoo import models, fields, api

class icon_settings(models.Model):
    _name = 'icon_settings'
    _description = '選舉地圖 座標設定'

    name = fields.Char('名稱')
    local_x = fields.Char('座標x')
    local_y = fields.Char('座標y')
    icon_url = fields.Char('icon_url設定')

'''
        iconUrl:"https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-black.png",
        shadowUrl:"https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
'''    