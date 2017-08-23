from odoo import api, fields, models
from datetime import datetime

class AssetManagementHandover (models.Model):
    _name = 'asset.management.handover'

    company_id = fields.Many2one ('res.partner', string = "Company", required = True)
    name = fields.Many2one ('hr.employee', string = "Employee", required = True)
    emp_email = fields.Char (string = "Email", readonly = True, related = 'name.user_id.login')
    source_loc = fields.Char (string = "Source Location", required = True)
    destination_loc = fields.Char (string = "Destination Location", required = True)
    date = fields.Date (string = "Date", default = lambda *a: datetime.today())
    transfer_type = fields.Char (string = "Transfer type", default = "Asset Handover", readonly = True)
    custodian_id = fields.Many2one ('res.users', string = "Custodian", readonly = True, default=lambda self: self.env.uid)
    processed_by = fields.Many2one ('hr.employee', string = "Processed by", readonly = True)
    internal_trans = fields.Char (string = "Internal Transfer", readonly = True)
    line_ids = fields.One2many('asset.handover.line', 'line_id')

    state = fields.Selection ([
        ('draft', "Draft"),
        ('transfer', "Transferred"),
        ('cancel', "Cancelled"),
    ], string = "State", default = 'draft')

    @api.multi
    def button_print(self):
        print 'print'

    @api.multi
    def button_email(self):
        print 'email'

    @api.multi
    def button_transfer(self):
        self.state = 'transfer'
        self.processed_by = self.env['hr.employee'].browse(self.env.uid)

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'
        self.processed_by = ''

class AssetHandoverLine (models.Model):
    _name = 'asset.handover.line'

    line_id = fields.Many2one ('asset.management.handover')
    change_location_id = fields.Many2one('asset.location.change')
    name = fields.Many2one('asset.asset', string = "Asset", required = True)
    asset_number = fields.Char(string = "Asset number", related = 'name.asset_number', readonly = True)
    model = fields.Many2one ('asset.model', string = "Model", required = True)
    purchase_date = fields.Date(string = "Purchase date", related = 'name.purchase_date', readonly = True)
    condition = fields.Many2one ('asset.condition', string = "Asset Condition", required = True)
    quantity = fields.Char (string = "Quantity", default = "1", required = True)