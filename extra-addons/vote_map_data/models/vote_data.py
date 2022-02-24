from odoo import models, fields, api

class vote_data(models.Model):
    _name = 'vote_data'
    _description = '中選會資料處理後'

    vote_type = fields.Char('選舉類別')
    city = fields.Char('縣市別')
    district = fields.Char('行政區別')
    data = fields.Char('得票資訊')
