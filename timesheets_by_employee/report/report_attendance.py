import pytz

from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ReportAttendance(models.AbstractModel):
    _name = 'report.timesheets_by_employee.report_attendance'

    def get_attendance_summary(self, docs):
        contract = self.env['hr.contract'].search([('partner_id','=',docs.company.id)], order='employee_id ASC')

        records=[]
        for contract in contract:
            print 'employee', contract.employee_id.name
            # timesheet_absent = self.env['hr_timesheet.summary'].search([('employee_id', '=', contract.employee_id.id),
            #                                                      ('date', '>=', docs.from_date),
            #                                                      ('date', '<=', docs.to_date),
            #                                                      ('duty_hours','!=',0)], order='date ASC')


            abs_count = 0
            total_late = 0
            total_ut = 0
            # for res in timesheet_absent:
            #     if res.actual_worked_hours == 0:
            #         abs_count += 1

            if contract.policy_id.id:
                policy_group_id = contract.policy_id.id

                self.env.cr.execute(
                    "SELECT group_id, absence_id from hr_policy_group_absence_rel where group_id = \'%s\'" % policy_group_id)
                res = self.env.cr.fetchall()
                print 'contracts>>>', res

                p_list = []
                for r in res:
                    print r[1]
                    p_list.append(r[1])
                print 'pList', p_list

                if contract.working_hours.work_type != 'flexi':
                    timesheet_sum = self.env['hr_timesheet.summary'].search([('employee_id', '=', contract.employee_id.id),
                                                                                 ('duty_hours', '!=', 0.00),
                                                                                 ('actual_worked_hours', '<', 8.00),
                                                                                 # ('diff', '<', 0.00),
                                                                                 ('date', '>=', docs.from_date),
                                                                                 ('date', '<=', docs.to_date)])

                    for rec in timesheet_sum:
                        print rec.date

                        if rec.actual_worked_hours:

                            absence_line = self.env['hr.policy.line.absence'].search(
                                [('use_late', '=', True),
                                 ('policy_id', 'in', p_list)])
                            late_min = 0.00
                            if absence_line:
                                _in = []
                                _out = []
                                sched_hrs = []

                                official_hours = self.env['resource.calendar.attendance'].search(
                                    [('calendar_id', '=', contract.working_hours.id)])

                                for id in official_hours:
                                    _in.append(id.hour_from)
                                    _out.append(id.hour_to)
                                    sched_hrs.append(id.sched_hours)

                                date = rec.date
                                dd = datetime.strptime(date, "%Y-%m-%d").date()
                                dt = datetime.strptime(date, "%Y-%m-%d")

                                attendance = self.env['hr.attendance'].search([('employee_id', '=', rec.employee_id.id),
                                                                               ('sheet_id', '=', rec.sheet_id.id)])

                                df = DEFAULT_SERVER_DATETIME_FORMAT
                                user_tz = self.env.user.tz or str(pytz.utc)
                                local = pytz.timezone(user_tz)

                                for res in attendance:
                                    check_in = datetime.strftime(
                                        pytz.utc.localize(datetime.strptime(res.check_in, df)).astimezone(local),
                                        "%Y-%m-%d %H:%M:%S")
                                    check_out = datetime.strftime(
                                        pytz.utc.localize(datetime.strptime(res.check_out, df)).astimezone(local),
                                        "%Y-%m-%d %H:%M:%S")

                                    check_in_date = datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S").date()
                                    check_out_date = datetime.strptime(check_out, "%Y-%m-%d %H:%M:%S").date()
                                    check_in_time = datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S").time()
                                    check_out_time = datetime.strptime(check_out, "%Y-%m-%d %H:%M:%S").time()

                                    if check_in_date == dd:

                                        hour = check_in_time.hour
                                        minute = check_in_time.minute
                                        # mins = round((check_in_time.minute % 1)*60)
                                        # minute = mins / 60

                                        actual_in = float('%s.%s' % (hour, minute))

                                        min = round((absence_line.active_after % 1) * 60)
                                        valid_min = min / 100
                                        # valid_min = min / 60


                                        if actual_in >= _in[0] and actual_in <= _out[0]:
                                            valid_hrs_in = _in[0] + valid_min
                                            diff = valid_hrs_in - actual_in

                                            if diff < 0:
                                                print 'LATE', diff
                                                print 'late date', check_in_date
                                                print 'late time', check_in_time
                                                late_min += minute


                                        elif actual_in >= _in[1] and actual_in <= _out[1]:
                                            valid_hrs_in = _in[1] + valid_min
                                            diff = valid_hrs_in - actual_in

                                            if diff < 0:
                                                print 'LATE', diff
                                                print 'late date', check_in_date
                                                print 'late time', check_in_time
                                                late_min += minute
                            if late_min:
                                if valid_min:
                                    remark = 'LATE'
                                    print 'REMARK', remark
                                    total_late += late_min

                            else:
                                # ut = ((rec.diff * 60) / 100)
                                ut = ((abs(rec.diff) * 60) / 100)
                                if ut > valid_min:
                                    remark = 'UT'
                                    print 'REMARK', remark

                                    total_ut += abs(rec.diff)

                        else:
                            holiday = self.env['hr.holidays.public.line'].search([('date', '=', rec.date)])
                            # holiday_type = self.env['hr.holidays.public.type'].browse(holiday)
                            if holiday:
                                remark = "HOL"
                                print 'REMARK', remark

                            else:
                                remark = "ABS"
                                print 'REMARK', remark
                                abs_count += 1

            vals = {'employee': contract.employee_id.name,
                    'absent':abs_count,
                    'late': total_late,
                    'undertime': total_ut,
                    }

            records.append(vals)
        return [records]


    @api.model
    def render_html(self, docids, data=None):
        """we are overwriting this function because we need to show values from other models in the report
        we pass the objects in the docargs dictionary"""

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        period = None
        _from = datetime.strptime(docs.from_date, "%Y-%m-%d").date()
        _to = datetime.strptime(docs.to_date, "%Y-%m-%d").date()

        _from_date = _from.strftime("%m-%d-%Y")
        _to_date=_to.strftime("%m-%d-%Y")

        if docs.from_date and docs.to_date:
            # period = "From " + str(docs.from_date) + " To " + str(docs.to_date)
            period = "From " + _from_date + " To " + _to_date
        elif docs.from_date:
            # period = "From " + str(docs.from_date)
            period = "From " + _from_date
        elif docs.from_date:
            # period = " To " + str(docs.to_date)
            period = " To " + _to_date

        attendance_summary = self.get_attendance_summary(docs)

        docargs = {
           'doc_ids': self.ids,
           'doc_model': self.model,
           'docs': docs,
           'period': period,
           'attendance':attendance_summary[0]
        }

        return self.env['report'].render('timesheets_by_employee.report_attendance', docargs)