from odoo import fields, api, models
from datetime import datetime
from odoo.exceptions import ValidationError

class CashAdvanceRequest (models.Model):
    _name = 'cash.advance.request'

    cash_amount = fields.Float (string = "Cash amount", required = True)
    date_requested = fields.Date (string = "Date", default = lambda *a: datetime.today())
    reason = fields.Text(string="Reason for Cash advance")

    employee_requested_id = fields.Many2one ('hr.employee', string = "Requested by", required = True)
    dept_id = fields.Many2one(string="Department", related='employee_requested_id.department_id', store=True, readonly=True)
    job_position_id = fields.Many2one(string="Job Position", related='employee_requested_id.job_id', store=True,readonly=True)

    lines_ids = fields.One2many('cash.advance.line.request', 'line_id')
    total_cash_amount = fields.Float(string="Total cash amount")

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

    @api.constrains('cash_amount')
    def check_amount(self):
        if self.cash_amount <= 0.00:
            raise ValidationError('Input amount not less than or equal to 0')

class AccountPettyCashLine (models.Model):
    _name = 'cash.advance.line.request'

    product_id = fields.Many2one ('product.product', string = "Product")

    cost = fields.Float(string = "Cost", related = 'product_id.standard_price')
    quantity = fields.Integer(default = "1")
    totalCost = fields.Float(string = "Total Cost")
    line_id = fields.Many2one('cash.advance.request')

    def on_change_total(self,cost,quantity):
	total_cost = cost * quantity
        res = {
            'value': {
                'totalCost': total_cost
	      }
	}
	return res



