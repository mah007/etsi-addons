from odoo import fields, api, models
from datetime import datetime
from odoo.exceptions import ValidationError

class PettyCashRequest (models.Model):
    _name = 'account.pettycash.request'

    amount = fields.Float (string = "Amount", required = True)
    date_requested = fields.Date (string = "Date", default = lambda *a: datetime.today())
    reason = fields.Text(string="Reason")

    employee_requested_id = fields.Many2one ('hr.employee', string = "Requested by", required = True)
    dept_id = fields.Many2one(string="Department", related='employee_requested_id.department_id', store=True, readonly=True)
    job_position_id = fields.Many2one(string="Job Position", related='employee_requested_id.job_id', store=True,readonly=True)

    lines_ids = fields.One2many('account.pettycash.line.request', 'line_id')
    total = fields.Float(string="Total amount")

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

    @api.constrains('amount')
    def check_amount(self):
        if self.amount <= 0.00:
            raise ValidationError('Input amount not less than or equal to 0')

class AccountPettyCashLine (models.Model):
    _name = 'account.pettycash.line.request'

    product_id = fields.Many2one ('product.product', string = "Product")

    cost = fields.Float(string = "Cost", related = 'product_id.standard_price')
    quantity = fields.Integer(default = "1")
    totalCost = fields.Float(string = "Total Cost")
    line_id = fields.Many2one('account.pettycash.request')
    # total = fields.Float(string="Total amount")

    # #This method will be called when quantity changes.
    def on_change_total(self,cost,quantity):
	#Calculate the total
	total_cost = cost * quantity
        res = {
            'value': {
		#This sets the total cost on the field total.
                'totalCost': total_cost
	      }
	}
	#Return the values to update it in the view.
	return res




