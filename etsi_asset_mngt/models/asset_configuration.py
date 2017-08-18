from odoo import api, fields, models

class AssetConfiguration(models.Model):
    _name = 'asset.config'

    serial_num = fields.Char(string="Serial #")
    name = fields.Char(string="Asset")
    asset_model = fields.Char(string="Model")
    year = fields.Date(string="Year")
    asset_condition = fields.Selection([('1', 'BRAND NEW'),
                                        ('2', 'USED'),
                                        ('3', 'DAMAGED')],
                                       string="Asset Condition")
    # quantity = fields.Float(string="Quantity")