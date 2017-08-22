from odoo import api, fields, models
from datetime import datetime

class AssetManagementReturn(models.Model):
    _name = 'asset.management.return'

    ret_company = fields.Many2one('res.partner', string="Company", required=True)
    ret_emp = fields.Many2one('hr.employee', string="Employee", required=True)
    ret_email = fields.Char(string="Email", readonly=True, related='ret_emp.user_id.login')
    ret_src_loc = fields.Char(string="Source Location", required=True)
    ret_des_loc = fields.Char(string="Destination Location", required=True)
    ret_date = fields.Date(string="Date", default=lambda *a: datetime.today())
    ret_transfer_type = fields.Char(string="Transfer type", default="Asset Return", readonly=True)
    ret_custodian = fields.Many2one('res.users', string="Custodian", default=lambda self: self.env.uid, readonly=True)
    ret_process_by = fields.Many2one('hr.employee', string="Processed by", readonly=True)
    ret_internal_trans = fields.Char(string="Internal Transfer", readonly=True)

#     ret_config_ids = fields.One2many('return.asset.config.inherit', 'ret_config_id', string="Asset's List")
#
# class AssetConfigInherit (models.Model):
#     _name = 'return.asset.config.inherit'
#
#     ret_config_id = fields.Many2one('asset.management.return')
#     ret_asset_id = fields.Many2one('asset.config', string="Asset", required=True)
#     ret_serial_num = fields.Char(string="Serial Number", related='ret_asset_id.serial_num', readonly=True)
#     ret_model = fields.Many2one('asset.model', string="Model", required=True)
#     ret_asset_year = fields.Date(string="Year", related='ret_asset_id.year', readonly = True)
#     ret_condition = fields.Many2one('asset.condition', string="Asset Condition", required=True)
#     ret_quantity = fields.Char(string="Quantity", default="1", required=True)