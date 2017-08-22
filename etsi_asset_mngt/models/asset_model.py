from odoo import api, fields, models

class AssetModel(models.Model):
    _name = 'asset.model'

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")