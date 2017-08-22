from odoo import fields, api, models

class AssetLocationChange(models.Model):
    _name = 'asset.location.change'

    company_id = fields.Many2one('res.partner', string="Company")
    destination_wh_id = fields.Char(string="Destination Warehouse")
    source_loc = fields.Char(string="Source Location")
    destination_loc = fields.Char(string="Destination Location")
    date_now = fields.Date(string="Date")
    transfer_type = fields.Selection([
                            ('asset_hanover', 'Asset Handover'),
                             ('asset_return', 'Asset Return'),
                             ('location_change', 'Asset Location Change')])
    it_engineer = fields.Char(string="IT Engineer")
    processed_by = fields.Char(string="Processed by")
    internal_transfer =fields.Char(string="Internal Transfer")
#     assets_ids = fields.One2many('asset.config','asset_loc_change_id',string="Assets")
#
# class AssetConfig(models.Model):
#     _inherit = 'asset.config'
#
    # asset_loc_change_id = fields.Many2one('asset.location.change', string="Asset Location Change")