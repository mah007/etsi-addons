from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
class Hr_Salary_Request(models.Model):
    _name = 'payroll.salary.request'
    _description = 'HR Salary Request'

    name = fields.Many2one('hr.employee',string="Employee", required=True)
    req_date = fields.Datetime(string="Request Date")
    req_amount = fields.Float(string="Request Amount")
    dept_ids = fields.Many2one('hr.department', string="Department")
    job_ids  = fields.Many2one('hr.job', string="Job Title")
    dept_manager = fields.Many2one('hr.employee', string="Department Manager")
    user_ids = fields.Many2one('res.users', string="Request User",default=lambda self: self.env.uid)
    confirmed_date=fields.Datetime(string="Confirmed Date")
    approved_date_dept = fields.Datetime(string="Approved Date (Department)")
    approved_date_hr = fields.Datetime(string="Approved Date (HR)")
    approved_date_bod = fields.Datetime(string="Approved Date (Director)")
    paid_date = fields.Datetime(string="Paid Date")
    confirm_by = fields.Many2one('hr.employee', string="Confirmed By")
    approve_by_dept = fields.Many2one('hr.employee', string="Department Manager")
    approve_by_hr= fields.Many2one('hr.employee', string="HR Manager")
    approve_by_bod = fields.Many2one('hr.employee', string="Director")
    paid_by = fields.Many2one('hr.employee', string="Paid By")
    company_ids = fields.Many2one('res.partner',string="Company",default=lambda self: self.env.user.company_id.id)
    refused_date = fields.Datetime(string="Refused Date")
    refused_by = fields.Many2one('hr.employee',string="Refused By")
    reason = fields.Text(string="Reason for Advance")
    comment = fields.Text(string="Comment")

    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('dept_approved', 'Approved by Department'),
                              ('hr_approved', 'Approved by HR'),
                              ('bod_approved', 'Approved by Director'),
                              ('paid', 'Paid'),
                              ('done', 'Done'),
                              ('refused','Refused'),], string="States", default='draft')

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'
        self.confirmed_date = datetime.today()
        self.confirm_by = self.env['hr.employee'].browse(self.env.uid)

    @api.multi
    def action_dept_approve(self):
        self.state = 'dept_approved'
        self.approved_date_dept = datetime.today()
        self.approve_by_dept = self.env['hr.employee'].browse(self.env.uid)

    @api.multi
    def action_hr_approve(self):
        self.state = 'hr_approved'
        self.approved_date_hr = datetime.today()
        self.approve_by_hr=self.env['hr.employee'].browse(self.env.uid)

    @api.multi
    def action_bod_approve(self):
        self.state = 'bod_approved'
        self.approved_date_bod = datetime.today()
        self.approve_by_bod= self.env['hr.employee'].browse(self.env.uid)

    @api.multi
    def action_paid(self):
        self.state = 'paid'
        self.paid_date = datetime.today()
        self.paid_by= self.env['hr.employee'].browse(self.env.uid)

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.multi
    def action_refused(self):
        self.state = 'refused'
        self.refused_date = datetime.today()
        self.refused_by = self.env['hr.employee'].browse(self.env.uid)

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        self.confirm_by =''
        self.confirmed_date=''

    @api.onchange('name')
    def _onchange_employee(self):
        selected_emp = self.name

        dept_id = self.env['hr.employee'].browse(selected_emp.department_id)
        self.dept_ids = dept_id.id

        job_id = self.env['hr.employee'].browse(selected_emp.job_id)
        self.job_ids = job_id.id

        mngr_id = self.env['hr.employee'].browse(selected_emp.parent_id)
        self.dept_manager = mngr_id.id
        print'>>',dept_id
