from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
import logging

_logger = logging.getLogger(__name__)
class HrAttendanceLogin(models.Model):
    _name = 'etsi.attendance.login'


    def _default_employee(self):
        emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    def _default_check_in_out(self):
        user_tz = self.env.user.tz or str(pytz.utc)
        local = pytz.timezone(user_tz)
        return datetime.strftime(pytz.utc.localize(datetime.today()).astimezone(local),'%H:%M:%S')


    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee)
    name = fields.Char(string="Name")
    attendance_state = fields.Selection([('checked_in','Check In'),
                                         ('checked_out','Checked Out')], string="Attendance State",  store=True)
    action = fields.Selection([('check_in','Check In'),
                               ('check_out','Check Out')], string="Action")
    check_in= fields.Char(string="Check In/Out", default=_default_check_in_out)
    check_out = fields.Char(string="Check In/Out", default=_default_check_in_out)
    ci_emp_name = fields.Char(string='Employee', related='employee_id.name_related')
    co_emp_name = fields.Char(string='Employee', related='employee_id.name_related')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        print 'change'
        self.attendance_state = self.employee_id.attendance_state

    @api.multi
    def act_sign_in_out(self):
        user_tz = self.env.user.tz or str(pytz.utc)
        local = pytz.timezone(user_tz)
        atndnce_state = self.attendance_state
        if atndnce_state == 'checked_out':
            self.env['hr.attendance'].create({'employee_id':self.employee_id.id,'check_in':datetime.today().strftime('%Y-%m-%d %H:%M:%S')})
            self.sudo().employee_id.attendance_state = 'checked_in'
            self.attendance_state = 'checked_in'
            self.check_in = datetime.strftime(pytz.utc.localize(datetime.today()).astimezone(local), '%H:%M:%S')

        else:
            res_atndnce = self.env['hr.attendance'].search([('employee_id','=', self.employee_id.id)])
            attendance_ids = res_atndnce.filtered(lambda r: not r.check_out and datetime.strftime(pytz.utc.localize(datetime.strptime(r.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(local),'%Y-%m-%d') == date.today().strftime('%Y-%m-%d'))
            for rec in attendance_ids:
                rec.write({'employee_id': self.employee_id.id, 'check_out': datetime.today().strftime('%Y-%m-%d %H:%M:%S')})
            self.sudo().employee_id.attendance_state = 'checked_out'

            self.attendance_state = 'checked_out'
            self.check_out = datetime.strftime(pytz.utc.localize(datetime.today()).astimezone(local),'%H:%M:%S')
        print 'self.employee_id.attendance_state', self.employee_id.attendance_state
        print 'self.attendance_state', self.attendance_state

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'etsi.attendance.login',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('etsi_hrms.etsi_attendance_greetings_form').id,
            'target': 'inline',
            'name': 'Attendance Greetings'
        }



    @api.multi
    def action_actual_time(self):
        context = {'employee_id': self.employee_id.id}
        print 'context', context
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'attendance.actual.time',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('etsi_hrms.attendance_actual_time_wizard').id,
            'target': 'new',
            'context': context,
            'name': 'Actual Time'
        }

    # @api.multi
    # def action_wz_confirm(self):
    #
    #     self.state = 'confirm'
    #
    #
    #     return {'type': 'ir.actions.act_window_close'}



class attendance_actual_time(models.Model):
    _name = 'attendance.actual.time'
    _inherit = ['mail.thread']
    _mail_post_access = 'read'


    def _default_employee(self):
        emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    employee_id = fields.Many2one('hr.employee',string='Employee', default=_default_employee)
    attendance_id = fields.Many2one('hr.attendance', string="Attendance")
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id', store=True)
    action = fields.Selection([('check_in','Check In'),('check_out','Check Out')], string="Action", default='check_in')
    date = fields.Date(string="Date", default=lambda *a:datetime.today())
    actual_time = fields.Float(string="Actual Time")
    reason = fields.Text(string="Reason")
    state = fields.Selection([('draft','Draft'),
                              ('confirm','Confirmed'),
                              ('approve','Approved'),
                              ('refuse', 'Refuse'),
                              ('void','Void'),
                              ('refuse','Refused')], string="Status", default='draft')

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            if rec.action == 'check_in':
                action = 'Check In'
            else:
                action = 'Check Out'
            name = "{} ({}/{})".format(rec.employee_id.name,rec.date,action)
            res.append((rec.id,name))
        return res


    @api.multi
    def action_wz_confirm(self):
        context = self.env.context
        self.employee_id = context['employee_id']
        self.state = 'confirm'

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirm'

    @api.multi
    def action_approve(self):
        dtf = DEFAULT_SERVER_DATETIME_FORMAT
        user_tz = self.env.user.tz or str(pytz.utc)
        local = pytz.timezone(user_tz)
        attendance_obj = self.env['hr.attendance']
        res_attendance = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id)])
        if res_attendance:
            # if self.action == 'check_in':
            res_attendance = res_attendance.filtered(lambda r: r.check_in and datetime.strftime(pytz.utc.localize(datetime.strptime(r.check_in,dtf),'%Y-%m-%d').astimezone(local), "%Y-%m-%d") == self.date)
            # else:
            #     res_attendance = res_attendance.filtered(lambda r: r.check_out and datetime.strftime(datetime.strptime(r.check_out,dtf), '%Y-%m-%d') == self.date)
            for rec in res_attendance:
                actual_time = attendance_obj.float_time_convert(self.actual_time) + ':00'
                get_dt =  datetime.strptime((self.date + ' '+ actual_time), dtf)
                tz_name = self.env.context.get('tz') or self.env.user.tz
                if tz_name:
                    try:
                        user_tz = pytz.timezone(tz_name)
                        utc = pytz.utc
                        actual_datetime = user_tz.localize(get_dt).astimezone(utc)
                    except Exception:
                        _logger.debug(
                            "failed to compute context/client-specific today date, using UTC value for `today`",
                            exc_info=True)

                    if self.action == 'check_in':
                        rec.write({'old_check_in':rec.check_in,'check_in':actual_datetime})
                    else:
                        rec.write({'old_check_out':rec.check_out,'check_out':actual_datetime})

                    self.attendance_id = rec.id
                    self.state = 'approve'

    @api.multi
    def action_refuse(self):
        self.state = 'refuse'

    @api.multi
    def action_void(self):
        if self.attendance_id:
            if self.action == 'check_in':
                self.attendance_id.write({'check_in':self.attendance_id.old_check_in})

        self.state = 'void'


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    old_check_in = fields.Datetime(string="Old Check In")
    old_check_out = fields.Datetime(string="Old Check Out")







