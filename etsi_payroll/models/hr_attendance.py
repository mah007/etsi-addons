import pytz
from datetime import datetime
import time
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Hr_Attendance(models.Model):
    _inherit ='hr.attendance'

    # late_hrs = fields.Float(string="Late",compute='_compute_late', store=True)

    # @api.depends('check_in','check_out')
    # def _compute_late(self):
    #     contract_id=self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)],order='id desc', limit=1)
    #
    #     for rec in contract_id:
    #         df = DEFAULT_SERVER_DATETIME_FORMAT
    #         user_tz = self.env.user.tz or str(pytz.utc)
    #         local = pytz.timezone(user_tz)
    #
    #         check_in = datetime.strftime(
    #             pytz.utc.localize(datetime.strptime(self.check_in, df)).astimezone(local),
    #             "%Y-%m-%d %H:%M:%S")
    #         check_out = datetime.strftime(
    #             pytz.utc.localize(datetime.strptime(self.check_out, df)).astimezone(local),
    #             "%Y-%m-%d %H:%M:%S")
    #
    #         print check_in
    #         print check_out


            # if rec.policy_ids.id:
            #     policy_group_id = rec.policy_ids.id
            #     print policy_group_id
            #     self.env.cr.execute(
            #         "SELECT group_id, absence_id from hr_policy_group_absence_rel where group_id = \'%s\'" % policy_group_id)
            #     res = self.env.cr.fetchall()
            #     print 'recs>>>', res
            #
            #     p_list = []
            #     for r in res:
            #         print r[1]
            #         p_list.append(r[1])
            #     print 'pList', p_list
            #
            #     official_hours = self.env['resource.calendar.attendance'].search(
            #         [('calendar_id', '=', rec.working_hours.id)])

                # for id in official_hours:
                #     _in.append(id.hour_from)
                #     _out.append(id.hour_to)
                #     sched_hrs.append(id.sched_hours)

    # @api.depends('check_in', 'check_out')
    # def _compute_worked_hours(self):
    #     for attendance in self:
    #         if attendance.check_out:
    #             delta = datetime.strptime(attendance.check_out, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(
    #                 attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
    #             attendance.worked_hours = delta.total_seconds() / 3600.0

