from odoo import api, fields, models
from datetime import datetime

class AssetManagementReturn(models.Model):
    _name = 'asset.management.return'

    ret_company = fields.Many2one('res.partner', string="Company")
    ret_emp = fields.Many2one('hr.employee', string="Employee")
    ret_email = fields.Char(string="Email")
    ret_src_loc = fields.Many2one('warehouse.config', string="Source Location")
    ret_des_loc = fields.Many2one('hr.employee', string="Destination Location")
    ret_date = fields.Date (string = "Date", default = lambda *a: datetime.today())
    ret_transfer_type = fields.Char(string="Transfer Type", default="Asset Return", readonly=True)
    ret_custodian = fields.Many2one('res.users', string="Custodian", default=lambda self: self.env.uid, readonly=True)
    ret_process_by = fields.Char(string="Processed by")
    ret_internal_trans = fields.Char(string="Internal Transfer")