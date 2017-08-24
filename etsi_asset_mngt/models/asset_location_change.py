from odoo import fields, api, models

class AssetLocationChange(models.Model):
    _name = 'asset.location.change'

    company_id = fields.Many2one('res.partner', string="Company")
    employee_id = fields.Many2one('asset.management.handover',string="Employee")
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
    change_location_ids = fields.One2many('asset.handover.line', 'change_location_id', string="Change Location Line")
    # assets_ids = fields.One2many('asset.config','asset_loc_change_id',string="Assets")

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            employee_id = self.env['asset.management.handover'].search([('id', '=', self.employee_id.id)])
            self.source_loc = employee_id.destination_loc
            employee_assets = self.env['asset.handover.line'].search([('line_id', '=', self.employee_id.id)])
            self.change_location_ids = employee_assets

# class AssetConfig(models.Model):
#     _inherit = 'asset.config'
#
#     asset_loc_change_id = fields.Many2one('asset.location.change', string="Asset Location Change")