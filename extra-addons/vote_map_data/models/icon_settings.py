from odoo import models, fields, api

class icon_settings(models.Model):
    _name = 'icon_settings'
    _description = '選舉地圖 座標設定'

    name = fields.Char('名稱')
    local_x = fields.Float('座標x',digits=(12,8))
    local_y = fields.Float('座標y',digits=(12,8))
    icon_url = fields.Char('icon_url設定')