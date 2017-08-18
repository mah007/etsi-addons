from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError

class AssetManagementHandover (models.Model):
    _name = 'asset.management.handover'

    company_id = fields.Many2one ('res.partner', string = "Company", required = True)
    emp_id = fields.Many2one ('hr.employee', string = "Employee", required = True)
    emp_email = fields.Char (string = "Email", readonly = True, related = 'emp_id.user_id.login')
    source_loc = fields.Char (string = "Source Location", required = True)
    destination_loc = fields.Char (string = "Destination Location", required = True)
    date = fields.Date (string = "Date", default = lambda *a: datetime.today())
    transfer_type = fields.Char (string = "Transfer type", default = "Asset Handover", readonly = True)
    custodian_id = fields.Many2one ('res.users', string = "Custodian", readonly = True, default=lambda self: self.env.uid)
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

    config_ids = fields.One2many ('asset.config.inherit', 'config_id', string = "Asset's List")


class AssetConfigInherit (models.Model):
    _name = 'asset.config.inherit'

    config_id = fields.Many2one ('asset.management.handover')
    asset_id = fields.Many2one('asset.config', string = "Asset", required = True)
    serial_num = fields.Char(string = "Serial #", related = 'asset_id.serial_num', readonly = True)
    model = fields.Many2one ('asset.model', string = "Model", required = True)
    asset_year  = fields.Date(string = "Year", related = 'asset_id.year', readonly = True)
    condition = fields.Many2one ('asset.condition', string = "Asset Condition", required = True)
    quantity = fields.Char (string = "Quantity", default = "1", required = True)