from odoo import api, fields, models
from datetime import datetime

class AssetManagementHandover (models.Model):
    _name = 'asset.management.handover'

    name = fields.Char(string = "Sequence")
    issuer_company_id = fields.Many2one ('res.partner', string = "Issuer's Company")
    issuer_id = fields.Many2one ('hr.employee', string = "Issuer's Name")
    issuer_email = fields.Char (string = "Email", readonly = True, related = 'issuer_id.user_id.login', store = True)
    source_loc = fields.Many2one ('stock.warehouse', string = "Source Location")

    recipient_company_id = fields.Many2one ('res.partner', string = "Recipient's Company")
    recipient_id = fields.Many2one ('hr.employee', string = "Recipient's Name")
    destination_loc = fields.Many2one ('stock.warehouse', string = "Destination Location")

    remarks = fields.Text (string = "Remarks")

    date = fields.Date (string = "Date", default = lambda *a: datetime.today())
    transfer_type = fields.Char (string = "Transfer type", default = "Asset Handover", readonly = True)
    custodian_id = fields.Many2one ('res.users', string = "Custodian", readonly = True, default=lambda self: self.env.uid)
    processed_by = fields.Many2one ('hr.employee', string = "Processed by", readonly = True)
    lines_ids = fields.One2many('asset.management.handover.lines', 'lines_id', string = " ")

    state = fields.Selection ([
        ('draft', "Draft"),
        ('transfer', "Transferred"),
        ('cancel', "Cancelled"),
    ], string = "State", default = 'draft')

    @api.onchange('issuer_company_id')
    def onchange_company(self):
        self.issuer_id = ''
        self.emp_email = ''
        self.source_loc = ''

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

class AssetManagementHandoverLine (models.Model):
    _name = 'asset.management.handover.lines'

    lines_id = fields.Many2one('asset.management.handover')
    asset_name_id = fields.Many2one('account.asset.asset', string = "Asset", required = True)
    serial_number_id = fields.Many2one('account.asset.asset.line', string = "Serial number", required = True)
    model = fields.Char (string = "Model", related = 'asset_name_id.model_id', store = True, readonly = True)
    condition_id = fields.Many2one ('asset.condition', string = "Asset Condition", required = True)
    state = fields.Char (string = "State")
    track_number = fields.Char (string = "Track Number")
    asset_pic = fields.Char(string="Asset picture")