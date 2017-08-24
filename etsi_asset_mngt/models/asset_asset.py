from odoo import api, fields, models

class AccountAssetAssetLine(models.Model):
    _name = 'account.asset.asset.line'

    serial_no_id = fields.Many2one('account.asset.asset',string="Serial Number")
    name = fields.Char(string="Serial Number")

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    serial_no_ids = fields.One2many('account.asset.asset.line','serial_no_id',string="Serial Number")
    model_id = fields.Char(string="Model")