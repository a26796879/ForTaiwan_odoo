from odoo import models, fields, api

class config_token(models.Model):
    _name = 'config_token'
    _description = 'line token設定'

    env_name = fields.Char('環境')
    line_token = fields.Char('token')