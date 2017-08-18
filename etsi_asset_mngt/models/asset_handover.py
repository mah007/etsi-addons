from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError

class AssetManagementHandover (models.Model):
    _name = 'asset.management.handover'

    company_id = fields.Many2one ('res.partner', string = "Company")
    emp_id = fields.Many2one ('hr.employee', string = "Employee")
    emp_email = fields.Char (string = "Email", readonly = True, related = 'emp_id.user_id.login')
    source_loc = fields.Char (string = "Source Location", readonly = True, related = 'company_id.name')
    destination_loc = fields.Char (string = "Destination Location", readonly = True, related = 'emp_id.name')
    date = fields.Date (string = "Date", default = lambda *a: datetime.today())
    transfer_type = fields.Char (string = "Transfer type", default = "Asset Handover", readonly = True)
    it_engineer_id = fields.Many2one ('res.users', string = "IT Engineer", readonly = True, default=lambda self: self.env.uid)
    processed_by = fields.Many2one ('hr.employee', string = "Processed by", readonly = True)
    internal_trans = fields.Char (string = "Internal Transfer", readonly = True)

    state = fields.Selection ([
        ('draft', "Draft"),
        ('transfer', "Transferred"),
        ('cancel', "Cancelled"),
    ], string = "State", default = 'draft')

    @api.multi
    def button_print(self):
        print 'print'
        raise ValidationError ("Mark inserted print function here")

    @api.multi
    def button_transfer(self):
        self.state = 'transfer'
        self.processed_by = self.env['hr.employee'].browse(self.env.uid)

    @api.multi
    def button_email(self):
        print 'email'
        raise ValidationError("Mark inserted email function here")

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'
        self.processed_by = ''

    config_ids = fields.One2many ('asset.config.inherit', 'config_id')


class AssetConfigInherit (models.Model):
    _name = 'asset.config.inherit'

    config_id = fields.Many2one ('asset.management.handover')
    asset_id = fields.Many2one('asset.config', string = "Asset", required = True)
    serial_num = fields.Char(string = "Serial #", related = 'asset_id.serial_num', readonly = True)
    model = fields.Many2one (string = "Model", related = 'asset_id.asset_model', readonly = True)
    asset_year  = fields.Date(string = "Year", related = 'asset_id.year', readonly = True)
    condition = fields.Char (string = "Asset Condition", readonly = True)
    quantity = fields.Char (string = "Quantity", default = "1")