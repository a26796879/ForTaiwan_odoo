from odoo import models, fields, api

class map_data(models.Model):
    _name = 'map_data'
    _description = '台灣鄉鎮區圖資存放'

    city = fields.Char('縣市別')
    district = fields.Char('行政區別')
    data = fields.Char('邊界座標')