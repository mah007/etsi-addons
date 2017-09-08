from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError

class AssetManagementReturn(models.Model):
    _name = 'asset.management.return'

    name = fields.Char(string=" ", readonly=True)
    ret_emp = fields.Many2one('hr.employee', string="Employee", required=True)
    ret_src_doc = fields.Many2one('asset.management.handover', string="Handover Order #", required=True)
    ret_email = fields.Char(string="Email")
    ret_src_loc = fields.Char(string="Source Location")
    ret_des_loc = fields.Char(string="Destination Location")
    ret_date = fields.Date(string="Date Return", default=lambda *a: datetime.today(), readonly=True)
    ret_transfer_type = fields.Char(string="Transfer type", default="Asset Return", readonly=True)
    ret_custodian = fields.Char(string="Issuer", readonly=True)
    ret_receive_by = fields.Many2one('hr.employee', string="Received by", readonly=True)
    ret_remarks = fields.Text(string="Remarks")

    return_ids = fields.One2many('asset.management.return.lines', 'ret_line_id', string="Asset")

    @api.onchange('ret_src_doc')
    def onchange_ret_src_doc(self):

        if self.ret_src_doc:
            source = self.env['asset.management.handover'].search([('id', '=', self.ret_src_doc.id)])
            self.ret_src_loc = source.source_loc.name
            self.ret_des_loc = source.destination_loc.name
            self.ret_custodian = source.issuer_id.name
            self.ret_email = source.recipient_email

    @api.onchange('ret_emp')
    def onchange_employee(self):
        self.ret_src_doc = 0

    #Generate button to create a copy of handover lines
    @api.multi
    def generate_asset(self):
        self.state = 'draft'
        assets_in_return = []
        collect_assets = self.env['asset.management.handover.lines'].search([('lines_id', '=', self.ret_src_doc.id)])
        assets_in = self.env['asset.management.return.lines'].search([('ret_line_id', '=', self.id)])
        print '>', collect_assets
        print '>>', assets_in

        for assets in assets_in:
            assets_in_return.append(assets.handover_line_id)
        print 'assets in', assets_in_return

        for c in collect_assets:
            if not c.ret_line_id:
                if c.id not in assets_in_return:
                    self.return_ids.create({
                        'ret_line_id': self.id,
                        'handover_line_id': c.id,
                        'ret_asset_name_id': c.asset_name_id.name,
                        'ret_serial_number_id': c.serial_number_id.name,
                        'ret_asset_serial_id': c.serial_number_id.id,
                        'ret_model': c.model,
                        'ret_condition_id': c.condition_id.name,
                    })
                else:
                    raise ValidationError("Error")

    #Create func for onchange values
    @api.model
    def create(self, vals):
        if vals.get('ret_emp'):
            vals.update({'ret_src_loc': self.env['asset.management.handover'].browse(
                vals.get('ret_src_doc')).source_loc.name})
            vals.update({'ret_des_loc': self.env['asset.management.handover'].browse(
                vals.get('ret_src_doc')).destination_loc.name})
            vals.update({'ret_custodian': self.env['asset.management.handover'].browse(
                vals.get('ret_src_doc')).issuer_id.name})
            vals.update({'ret_email': self.env['asset.management.handover'].browse(
                vals.get('ret_src_doc')).recipient_email})


        vals['name'] = self.env['ir.sequence'].next_by_code('return.seq.views')

        return super(AssetManagementReturn, self).create(vals)

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('received', "Received"),
        ('cancel', "Cancelled"),
    ], string="State", default='draft')

    @api.multi
    def button_draft(self):
        self.state = 'draft'

    @api.multi
    def button_confirmed(self):
        self.state = 'confirmed'
        if not self.return_ids:
            raise ValidationError('Generate Assets first. No assets to be return.')

    #Button to compare created return lines to handover lines
    @api.multi
    def button_received(self):
        self.state = 'received'
        self.ret_receive_by = self.env['hr.employee'].browse(self.env.uid)

        ret_handover = []
        ret_return =[]
        ret_return_filter = []

        ret_handover_line = self.env['asset.management.handover.lines'].search([('lines_id', '=', self.ret_src_doc.id)])
        ret_return_line = self.env['asset.management.return.lines'].search([('ret_line_id', '=', self.id)])
        ret_filter = self.env['asset.management.return.lines'].search([('id', '>', 0)])

        for a in ret_handover_line:
            ret_handover.append(a.id)
            print 'a', a

        for b in ret_return_line:
            ret_return.append(b.handover_line_id)
            print 'b', b

        for d in ret_filter:
            ret_return_filter.append(d.handover_line_id)
            print 'd', d

        print 'hand over line', ret_handover_line
        print 'return line, ', ret_return_line
        print 'ret filter', ret_filter

        total = set(ret_handover).intersection(ret_return)
        print 'total', total

        ret_filter_value = len(ret_return_filter) != len(set(ret_return_filter))

        print '>', ret_return_filter
        print '>>', len(ret_return_filter) != len(set(ret_return_filter))
        print '>>>', ret_return
        print '>>>>', ret_handover

        for c in ret_handover_line:

            if ret_filter_value == True:
                raise ValidationError('Two Return Sequence have the same assets to be return. Please delete the other one.')
            else:
                if c.id in total:
                    c.ret_line_id = self.id
                    c.serial_number_id.asset_serial_state = True
                    print '>: nareturn na sya'

        asset_history = self.env['asset.management.history'].search([('handover_no', '=', self.ret_src_doc.name)])
        # asset_serial = self.return_ids.ret_serial_number_id
        asset_serial_list = []
        # asset_serial_list.append(self.return_ids.ret_serial_number_id)
        for i in self.return_ids:
            asset_serial_list.append(i.ret_serial_number_id)
        for a in asset_history:
            if a.serial_number_id.name in asset_serial_list:
                a.date_return = self.ret_date
                a.received_by_name_id = self.ret_receive_by

    @api.multi
    def button_email(self):
        template = self.env.ref('etsi_asset_mngt.example_email_template1')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'
        self.ret_receive_by = ''

        ret_handover = []
        ret_return = []

        ret_handover_line = self.env['asset.management.handover.lines'].search([('lines_id', '=', self.ret_src_doc.id)])
        ret_return_line = self.env['asset.management.return.lines'].search([('ret_line_id', '=', self.id)])

        for a in ret_handover_line:
            ret_handover.append(a.id)

        for b in ret_return_line:
            ret_return.append(b.handover_line_id)

        total = set(ret_handover).intersection(ret_return)
        print 'total', total

        for c in ret_handover_line:
            if c.id in total:
                c.ret_line_id = ''
                c.serial_number_id.asset_serial_state = False
                print '>: nabago na sya'

class AssetHandoverLine(models.Model):
    _name = 'asset.management.return.lines'

    ret_line_id = fields.Many2one('asset.management.return', ondelete='cascade')
    handover_line_id = fields.Integer(string="Handover ID")
    ret_asset_name_id = fields.Char(string="Asset")
    ret_serial_number_id = fields.Char(string="Serial number")
    ret_asset_serial_id = fields.Char(string="Asset Serial ID")
    ret_model = fields.Char(string="Model")
    ret_condition_id = fields.Char(string="Asset Condition")
    ret_asset_pic = fields.Char(string="Asset picture")
