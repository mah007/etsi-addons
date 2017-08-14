from odoo import fields, api, models
from datetime import datetime

class PettyCashRequest (models.Model):
    _name = 'account.pettycash.request'

    amount = fields.Float (string = "Amount")
    date_requested = fields.Date (string = "Date", default = lambda *a: datetime.today())
    reason = fields.Text(string="Reason")

    employee_requested_id = fields.Many2one ('hr.employee', string = "Requested by")
    dept_id = fields.Many2one(string="Department", related='employee_requested_id.department_id', store=True, readonly=True)
    job_position_id = fields.Many2one(string="Job Position", related='employee_requested_id.job_id', store=True,readonly=True)

    lines_ids = fields.One2many('account.pettycash.line.request', 'line_id')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Aprroved")], default='draft')

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def action_approve(self):
        self.state = 'approved'

class AccountPettyCashLine (models.Model):
    _name = 'account.pettycash.line.request'

    product_id = fields.Many2one ('product.product', string = "Product")

    cost = fields.Float(string = "Cost", related = 'product_id.standard_price')
    quantity = fields.Integer(default = "1")

    line_id = fields.Many2one ('account.pettycash.request')

