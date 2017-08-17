from odoo import api, fields, models
from datetime import datetime

class AssetManagementHandover (models.Model):
    _name = 'asset.management.handover'

    company_id = fields.Many2one ('res.partner', string = "Company")
    emp_id = fields.Many2one ('hr.employee', string = "Employee")
    emp_email = fields.Char (string = "Email", readonly = True)
    source_loc = fields.Char (string = "Source Location", readonly = True)
    destination_loc = fields.Char (string = "Destination Location", readonly = True)
    date = fields.Date (string = "Date", default = lambda *a: datetime.today())
    transfer_type = fields.Char (string = "Transfer type")
    it_engineer = fields.Char (string = "IT Engineer")
    processed_by = fields.Char (string = "Processed by")
    internal_trans = fields.Char (string = "Internal Transfer")