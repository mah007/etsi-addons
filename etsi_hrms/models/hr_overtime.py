from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
import math
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Hr_Overtime_Details(models.Model):
    _name = 'hr.overtime.det'
    _description = 'HR Overtime Details'
    _inherit = ['mail.thread']

    overtime_id = fields.Many2one('hr.overtime', string="Overtime")
    start_time = fields.Float(string="Start Time")
    end_time = fields.Float(string="End Time")
    numofhours = fields.Float(string="Number of Hours", digits=(16, 2), compute='_compute_numofhours', store=True)

    @api.depends('start_time', 'end_time')
    def _compute_numofhours(self):
        for ot in self:
            if ot.start_time and ot.end_time:
                numhours = ot.end_time - ot.start_time
                ot.numofhours = numhours


class Hr_Overtime(models.Model):
    _name = 'hr.overtime'
    _description = 'HR Overtime'
    _inherit = ['mail.thread']

    def _default_employee(self):
        emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee)
    employee_ids = fields.Many2many('hr.employee', 'overtime_employee_rel', 'overtime_id', 'employee_id', string="Employees", ondelete='cascade')
    start_date = fields.Date(string="Start Date",  default= lambda *a: datetime.today())
    end_date = fields.Date(string="End Date", default= lambda *a: datetime.today())
    start_time = fields.Float(string="Start Time")
    end_time = fields.Float(string="End Time")
    dept_id = fields.Many2one('hr.department', string="Department")
    dep_manager_id = fields.Many2one('hr.employee', string="Manager")
    purpose = fields.Text(string="Purpose")
    include_payroll = fields.Boolean(string="Include in Payroll", default=True)
    mngr_aprvd_date = fields.Date(string='Approved Date')
    hr_aprvd_date = fields.Date(string="HR Approved Date")
    hr_aprvd_by = fields.Many2one('hr.employee', string="HR Approved By")
    numofhours = fields.Float(string="Number of Hours", digits=(16, 2), compute='_compute_numofhours', store=True)
    ot_req_type = fields.Selection([('by_employee','By Employee'),
                                    ('by_department', 'By Department'),], string="Request Type", default='by_employee')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting for Department Approval'),
                              ('approve', 'Approved'),
                              ('refuse', 'Refused'),
                              ('void', 'Void')],  track_visibility='onchange', string="States", default='draft')
    overtime_det_ids = fields.One2many('hr.overtime.det', 'overtime_id', string="Overtime Details")


    @api.multi
    def action_confirm(self):
        self.state = 'confirm'

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_approve(self):
        self.state = 'approve'

    @api.multi
    def action_refuse(self):
        self.state = 'refuse'

    @api.multi
    def action_void(self):
        self.state = 'void'

    @api.onchange('ot_req_type')
    def onchange_ot_req_type(self):
        if self.ot_req_type == 'by_department':
            self.employee_id = False
        self.write({'employee_ids': [(5)]})

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            dept_id = self.employee_id.department_id
            if dept_id:
                self.dept_id = dept_id
            else:
                raise ValidationError("No Department Assigned for the Specified Employee")

    @api.onchange('employee_ids')
    def onchange_employee_ids(self):
        if self.ot_req_type == 'by_department':
            if not self.dept_id:
                raise ValidationError("Please fill Department field first.")

    @api.onchange('dept_id')
    def onchange_dept_id(self):
        if self.dept_id:
            res_emp = self.env['hr.employee'].search([('department_id','=',self.dept_id.id)])
            emp_ids = []
            for rec_emp in res_emp:
                emp_ids.append(rec_emp.id)

            return {'domain': {'employee_ids': [('id', 'in', emp_ids)]}}

    @api.depends('start_time','end_time')
    def _compute_numofhours(self):
        for ot in self:
            user_tz = self.env.user.tz or pytz.utc
            local = pytz.timezone(user_tz)
            if ot.start_time and ot.end_time:
                numhours = ot.end_time - ot.start_time
                ot.numofhours = numhours


    ####################################################
    # Messaging methods
    ####################################################

    @api.multi
    def _track_subtype(self, init_values):
        if 'state' in init_values and self.state == 'confirm':
            return 'etsi_hrms.mt_overtime_confirmed'
        elif 'state' in init_values and self.state == 'approve':
            return 'etsi_hrms.mt_overtime_approved'
        elif 'state' in init_values and self.state == 'refuse':
            return 'etsi_hrms.mt_overtime_refused'
        return super(Hr_Overtime, self)._track_subtype(init_values)

    # @api.multi
    # def _notification_recipients(self, message, groups):
    #     print 'groups', groups










def seconds(td):
    assert isinstance(td, timedelta)
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10.**6