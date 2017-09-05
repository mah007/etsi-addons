from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError

class AssetManagementHandover (models.Model):
    _name = 'asset.management.handover'

    name = fields.Char(string = " ", readonly = True)
    issuer_company_id = fields.Many2one ('res.partner', string = "Issuer's Company", required = True)
    issuer_id = fields.Many2one ('hr.employee', string = "Issuer's Name", required = True)
    source_loc = fields.Many2one ('stock.warehouse', string = "Source Location", required = True)

    recipient_company_id = fields.Many2one ('res.partner', string = "Recipient's Company", required = True)
    recipient_id = fields.Many2one ('hr.employee', string = "Recipient's Name", required = True)
    recipient_email = fields.Char(string="Email", readonly=True, related='recipient_id.user_id.login', store=True)
    destination_loc = fields.Many2one ('stock.warehouse', string = "Destination Location", required = True)

    remarks = fields.Text (string = "Remarks")

    date = fields.Date (string = "Date", default = lambda *a: datetime.today())
    transfer_type = fields.Char (string = "Transfer type", default = "Asset Handover", readonly = True)
    processed_by = fields.Many2one ('hr.employee', string = "Approved by", readonly = True)
    lines_ids = fields.One2many('asset.management.handover.lines', 'lines_id', string = " ")


    state = fields.Selection ([
        ('draft', "Draft"),
        ('confirm', 'Waiting for approval'),
        ('approve', 'Approved'),
        ('transfer', "Transferred"),
        ('cancel', "Cancelled"),
    ], string = "State", default = 'draft')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('handover.seq.views')
        return super(AssetManagementHandover, self).create(vals)

    @api.onchange('issuer_company_id')
    def onchange_issuer_company(self):
        self.issuer_id = ''
        self.emp_email = ''
        self.source_loc = ''

    @api.onchange('recipient_company_id')
    def onchange_recipient_company(self):
        self.recipient_id = ''
        self.destination_loc = ''

    @api.multi
    def button_draft(self):
        self.state = 'draft'

    @api.multi
    def button_confirm(self):
        self.state = 'confirm'
        if not self.lines_ids:
            raise ValidationError ('Please select your asset before the confirmation of your transaction')

    @api.multi
    def button_approve(self):
        self.state = 'approve'
        for assets in self.lines_ids:
            if assets.serial_number_id.asset_serial_state == False:
                raise ValidationError ('Error')


    @api.multi
    def button_transfer(self):
        self.state = 'transfer'
        self.processed_by = self.env['hr.employee'].browse(self.env.uid)

        asset_line = self.env['asset.management.handover.lines'].search([('lines_id', '=', self.id)])
        print '>', asset_line

        for asset in asset_line:
            asset.serial_number_id.asset_serial_state = False

    @api.multi
    def button_email(self):
        print 'hehe'

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'
        self.processed_by = ''

        for assets in self.lines_ids:
            assets.serial_number_id.asset_serial_state = True

class AssetManagementHandoverLine (models.Model):
    _name = 'asset.management.handover.lines'

    lines_id = fields.Many2one('asset.management.handover')
    asset_name_id = fields.Many2one('account.asset.asset', string = "Asset", required = True)
    serial_number_id = fields.Many2one('account.asset.asset.line', string = "Serial number", required = True)
    model = fields.Char (string = "Model", related = 'asset_name_id.model_id', store = True, readonly = True)
    condition_id = fields.Many2one ('asset.condition', string = "Asset Condition", required = True)
    asset_pic = fields.Many2many('ir.attachment', string = "Asset picture")
    total = fields.Integer(string = "Total", default = "1")
    ret_line_id = fields.Many2one('asset.management.return', string="Return ID", readonly=True)

    @api.onchange('asset_name_id')
    def on_change_asset_name(self):
        self.serial_number_id = ''

