from odoo import api, fields, models

class AssetCondition(models.Model):
    _name = 'asset.condition'

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")