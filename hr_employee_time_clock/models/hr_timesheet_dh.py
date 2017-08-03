# -*- coding: utf-8 -*-

##############################################################################
#
#    Clear Groups for Odoo
#    Copyright (C) 2016 Bytebrand GmbH (<http://www.bytebrand.net>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pytz
import time
from datetime import datetime, timedelta, date
from odoo import api, fields, models, _
from dateutil import rrule, parser, tz
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.tz import tzutc, tzlocal
from odoo.exceptions import ValidationError



class HrTimesheetSheet(models.Model):
    """
        Addition plugin for HR timesheet for work with duty hours
    """
    _inherit = 'hr_timesheet_sheet.sheet'

    @api.multi
    def _duty_hours(self):
        for sheet in self:
            sheet['total_duty_hours'] = 0.0
            if sheet.state == 'done':
                sheet['total_duty_hours'] = sheet.total_duty_hours_done
            else:
                dates = list(rrule.rrule(rrule.DAILY,
                                         dtstart=parser.parse(sheet.date_from),
                                         until=parser.parse(sheet.date_to)))
                period = {'date_from': sheet.date_from,
                          'date_to': sheet.date_to}
                for date_line in dates:
                    duty_hours = sheet.calculate_duty_hours(date_from=date_line,
                                                            period=period,
                                                            )

                    sheet['total_duty_hours'] += duty_hours
                sheet['total_duty_hours'] = (sheet.total_duty_hours -
                                             sheet.total_attendance)

    @api.multi
    def count_leaves(self, date_from, employee_id, period):
        df = DEFAULT_SERVER_DATETIME_FORMAT
        user_tz = self.env.user.tz or str(pytz.utc)
        local = pytz.timezone(user_tz)
        holiday_obj = self.env['hr.holidays']
        start_leave_period = end_leave_period = False
        if period.get('date_from') and period.get('date_to'):
            start_leave_period = period.get('date_from')
            end_leave_period = period.get('date_to')

        holiday_ids = holiday_obj.search(
            ['|', '&',
             ('date_from', '>=', start_leave_period),
             ('date_from', '<=', end_leave_period),
             '&', ('date_to', '<=', end_leave_period),
             ('date_to', '>=', start_leave_period),
             ('employee_id', '=', employee_id),
             ('state', '=', 'validate'),
             ('type', '=', 'remove')])

        leaves = []
        for leave in holiday_ids:
            date_from_leave = datetime.strftime(pytz.utc.localize(datetime.strptime(leave.date_from, df)).astimezone(local), "%Y-%m-%d %H:%M:%S")
            date_to_leave = datetime.strftime(pytz.utc.localize(datetime.strptime(leave.date_to, df)).astimezone(local),"%Y-%m-%d %H:%M:%S")

            leave_date_from = datetime.strptime(date_from_leave,
                                                '%Y-%m-%d %H:%M:%S')
            leave_date_to = datetime.strptime(date_to_leave,
                                              '%Y-%m-%d %H:%M:%S')
            leave_dates = list(rrule.rrule(rrule.DAILY,
                                           dtstart=parser.parse(
                                               date_from_leave),
                                           until=parser.parse(date_to_leave)))
            for date in leave_dates:
                if date.strftime('%Y-%m-%d') == date_from.strftime('%Y-%m-%d'):
                    leaves.append(
                        (leave_date_from, leave_date_to, leave.number_of_days))
                    break

        return leaves

    @api.multi
    def get_overtime(self, start_date):
        for sheet in self:
            if sheet.state == 'done':
                return sheet.total_duty_hours_done * -1
            return self.calculate_diff(start_date)

    @api.multi
    def _overtime_diff(self):
        for sheet in self:
            old_timesheet_start_from = parser.parse(
                sheet.date_from) - timedelta(days=1)
            prev_timesheet_diff = \
                self.get_previous_month_diff(
                    sheet.employee_id.id,
                    old_timesheet_start_from.strftime('%Y-%m-%d')
                )
            sheet['calculate_diff_hours'] = (
                self.get_overtime(datetime.today().strftime('%Y-%m-%d'), ) +
                prev_timesheet_diff)
            sheet['prev_timesheet_diff'] = prev_timesheet_diff

    @api.multi
    def _get_analysis(self):
        res = {}
        contract_obj = self.env['hr.contract']
        attendance_obj = self.env['hr.attendance']
        emp_id = self.employee_id.id
        duty_hours = 0.0
        contract_obj = self.env['hr.contract']
        contract_ids = contract_obj.search([
            ('employee_id', '=', emp_id),
            ('date_start', '<=', self.date_from),
            '|',
            ('date_end', '>=', self.date_to),
            ('date_end', '=', None)
        ])
        if not contract_ids:
            raise ValidationError('No contract created for the assigned employee')

        for contract in contract_ids:
            work_type = contract.working_hours.work_type

        for sheet in self:
            function_call = True

            data = self.attendance_analysis(sheet.id, function_call)
            values = []
            output = [
                '<style>.attendanceTable td,.attendanceTable th {padding: 6px; border: 1px solid #C0C0C0; text-align: right;} </style><table class="attendanceTable" >']
            if work_type != 'flexi':
                for val in data.values():
                    if isinstance(val, (int, float)):
                        output.append('<tr>')
                        output.append('<th style="text-align:center">' + 'DATE' + ' </th>')
                        output.append('<th colspan="2" style="text-align:center;font-weight:bold">' + 'DUTY HOURS' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + 'Sched Hours' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th colspan="3" style="text-align:center">' + 'WORKED HOURS' + '</th>')
                        output.append('<th style="text-align:center">' + 'DIFFERENCE' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th colspan="3" style="text-align:center">' + 'AUTHORIZED OT' + '</th>')
                        output.append('<th style="text-align:center">' + 'ACTUAL OT' + '</th>')
                        output.append('<th style="text-align:center">' + 'ACTUAL WH' + '</th>')
                        output.append('<th style="text-align:center">' + 'REMARKS' + '</th>')
                        output.append('</tr>')

                for k, v in data.items():
                    if isinstance(v, list):
                        output.append('<tr>')
                        output.append('<th>' + ''+ '</th>')
                        output.append('<th>' + 'From' + '</th>')
                        output.append('<th>' + 'To' + '</th>')
                        # output.append('<th>' + 'Hours' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + 'From' + '</th>')
                        output.append('<th>' + 'To' + '</th>')
                        output.append('<th>' + 'Hours' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + 'From' + '</th>')
                        output.append('<th>' + 'To' + '</th>')
                        output.append('<th>' + 'Hours' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        #
                        # for th in v[0].keys():
                        #     output.append('<th>' + th + '</th>')
                        output.append('</tr>')

                        for res in v:
                            output.append('<tr>')
                            output.append('<td>' + res['Date'] + '</td>')
                            output.append('<td>' + res['Duty From'] + '</td>')
                            output.append('<td>' + res['Duty To'] + '</td>')
                            # output.append('<td>' + res['Duty Hours'] + '</td>')
                            output.append('<td>' + '' + '</td>')
                            output.append('<td style="text-align:center">' + res['Sched Hours'] + '</td>')
                            output.append('<td>' + '' + '</td>')
                            output.append('<td>' + res['Worked From'] + '</td>')
                            output.append('<td>' + res['Worked To'] + '</td>')
                            output.append('<td>' + res['Worked Hours'] + '</td>')
                            output.append('<td style="text-align:center">' + res['Difference'] + '</td>')
                            output.append('<td>' + '' + '</td>')
                            output.append('<td>' + res['OT From'] + '</td>')
                            output.append('<td>' + res['OT To'] + '</td>')
                            output.append('<td>' + res['auth_ot_hour'] + '</td>')
                            output.append('<td style="text-align:center">' + res['actual_ot'] + '</td>')
                            output.append('<td style="text-align:center">' + res['actual_wh'] + '</td>')
                            output.append('<td style="text-align:left">' + res['Remarks'] + '</td>')
                            output.append('</tr>')
                        for tr in values:
                            output.append('<tr>')
                            for td in tr:
                                output.append('<td>' + td + '</td>')
                            output.append('</tr>')
                    if isinstance(v, dict):
                        output.append('<tr>')
                        total_ts = _('Total:')
                        output.append('<th style="text-align:left">' + total_ts + ' </th>')
                        output.append('<th' + '' + ' </th>')
                        output.append('<th' + '' + ' </th>')
                        output.append('<th' + '' + ' </th>')
                        output.append('<th style="text-align:center">' + '%s' % attendance_obj.float_time_convert(v['duty_hours']) + '</th>')
                        output.append('<th >' + '' + ' </th>')
                        output.append('<th' + '' + ' </th>')
                        output.append('<th>' + '' + ' </th>')
                        output.append('<th>' + '%s' % attendance_obj.float_time_convert(v['worked_hours']) + ' </th>')
                        output.append('<th style="text-align:center">' + '%s' % attendance_obj.float_time_convert(v['diff']) + ' </th>')
                        output.append('<th>' + '' + ' </th>')
                        output.append('<th>' + '' + ' </th>')
                        output.append('<th' + '' + ' </th>')
                        output.append('<th>' + '%s' % attendance_obj.float_time_convert(v['auth_ot']) + ' </th>')
                        output.append('<th style="text-align:center">' + '%s' % attendance_obj.float_time_convert(v['actual_ot']) + ' </th>')
                        output.append('<th style="text-align:center">' + '%s' % attendance_obj.float_time_convert(v['actual_worked_hours']) + '</th>')
                        output.append('<th>' + '' + ' </th>')
                        output.append('</tr>')
                output.append('</table>')

            #If work_type == 'flexi'
            else:
                for val in data.values():
                    if isinstance(val, (int, float)):
                        output.append('<tr>')
                        output.append('<th style="text-align:center">' + 'DATE' + ' </th>')
                        output.append('<th colspan="2" style="text-align:center;font-weight:bold">' + 'DUTY HOURS' + '</th>')
                        output.append('<th style="text-align:center;font-weight:bold">' + 'SCHED HOURS' + '</th>')
                        output.append('<th colspan="3" style="text-align:center;font-weight:bold">' + 'CORE HOURS' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th colspan="3" style="text-align:center">' + 'WORKED HOURS' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th style="text-align:center">' + 'CORE WORKED' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th colspan="3" style="text-align:center">' + 'AUTHORIZED OT' + '</th>')
                        output.append('<th style="text-align:center">' + 'ACTUAL OT' + '</th>')
                        output.append('<th style="text-align:center">' + 'ACTUAL WH' + '</th>')
                        output.append('<th style="text-align:center">' + 'REMARKS' + '</th>')
                        output.append('</tr>')

                for k, v in data.items():
                    if isinstance(v, list):
                        output.append('<tr>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + 'From' + '</th>')
                        output.append('<th>' + 'To' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + 'From' + '</th>')
                        output.append('<th>' + 'To' + '</th>')
                        output.append('<th>' + 'Hours' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + 'From' + '</th>')
                        output.append('<th>' + 'To' + '</th>')
                        output.append('<th>' + 'Hours' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + 'From' + '</th>')
                        output.append('<th>' + 'To' + '</th>')
                        output.append('<th>' + 'Hours' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('</tr>')

                        for res in v:
                            output.append('<tr>')
                            output.append('<td>' + res['Date'] + '</td>')
                            output.append('<td>' + res['Duty From'] + '</td>')
                            output.append('<td>' + res['Duty To'] + '</td>')
                            output.append('<td style="text-align:center">' + res['Sched Hours'] + '</td>')
                            output.append('<td>' + res['Core Hours From'] + '</td>')
                            output.append('<td>' + res['Core Hours To'] + '</td>')
                            output.append('<td>' + res['Core Hours'] + '</td>')
                            output.append('<td>' + '' + '</td>')
                            output.append('<td>' + res['Worked From'] + '</td>')
                            output.append('<td>' + res['Worked To'] + '</td>')
                            output.append('<td>' + res['Worked Hours'] + '</td>')
                            output.append('<td>' + '' + '</td>')
                            output.append('<td style="text-align:center">' + res['Core Worked'] + '</td>')
                            output.append('<th>' + '' + '</th>')
                            output.append('<td>' + res['OT From'] + '</td>')
                            output.append('<td>' + res['OT To'] + '</td>')
                            output.append('<td>' + res['auth_ot_hour'] + '</td>')
                            output.append('<td style="text-align:center">' + res['actual_ot'] + '</td>')
                            output.append('<td style="text-align:center">' + res['actual_wh'] + '</td>')
                            output.append('<td style="text-align:left">' + res['Remarks'] + '</td>')
                            output.append('</tr>')

                    if isinstance(v, dict):
                        output.append('<tr>')
                        total_ts = _('Total:')
                        output.append('<th style="text-align:left">' + total_ts + ' </th>')
                        output.append('<th colspan="2">' + '' +  '</th>')
                        output.append('<th style="text-align:center">' + '%s' % attendance_obj.float_time_convert(v['duty_hours']) + '</th>')
                        output.append('<th colspan="2">' + '' + '</th>')
                        output.append('<th style="text-align:center">' + '%s' % attendance_obj.float_time_convert(v['core_hours']) + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th colspan="2">' + '' + '</th>')
                        output.append('<th style="text-align:center">' + '%s' % attendance_obj.float_time_convert( v['worked_hours']) + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th style="text-align:center">' + '%s' % attendance_obj.float_time_convert(v['core_worked']) + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('<th colspan="2">' + '' + '</th>')
                        output.append('<th style="text-align:center">' + '%s' % attendance_obj.float_time_convert(v['auth_ot']) + '</th>')
                        output.append('<th style="text-align:center">' + '%s' % attendance_obj.float_time_convert(v['actual_ot']) + '</th>')
                        output.append('<th style="text-align:center">' + '%s' % attendance_obj.float_time_convert(v['actual_worked_hours']) + '</th>')
                        output.append('<th>' + '' + '</th>')
                        output.append('</tr>')
                output.append('</table>')


            sheet['analysis'] = '\n'.join(output)

    total_duty_hours = fields.Float(compute='_duty_hours',
                                    string='Total Duty Hours',
                                    multi="_duty_hours")
    total_duty_hours_done = fields.Float(string='Total Duty Hours',
                                         readonly=True,
                                         default=0.0)
    total_diff_hours = fields.Float(string='Total Diff Hours',
                                    readonly=True,
                                    default=0.0)
    calculate_diff_hours = fields.Char(compute='_overtime_diff',
                                       string="Diff (worked-duty)",
                                       multi="_diff")
    prev_timesheet_diff = fields.Char(compute='_overtime_diff',
                                      method=True,
                                      string="Diff from old",
                                      multi="_diff")
    analysis = fields.Text(compute='_get_analysis',
                           type="text",
                           string="Attendance Analysis")

    @api.multi
    def calculate_duty_hours(self, date_from, period):
        contract_obj = self.env['hr.contract']
        calendar_obj = self.env['resource.calendar']
        emp_id = self.employee_id.id
        duty_hours = 0.0
        contract_ids = self.get_contract(emp_id, date_from)
        for contract in contract_ids:
            ctx = dict(self.env.context).copy()
            ctx.update(period)
            work_type = contract.working_hours.work_type
            calendar_id = contract.working_hours.id
            if work_type == 'weekly':
                dayweek = date_from.weekday()
                cal_att_ids = self.env['resource.calendar.attendance'].search([('calendar_id', '=', calendar_id), ('dayofweek', '=', dayweek)])
                dh = 0
                for cal_att in cal_att_ids:
                    dh += cal_att.sched_hours


            elif work_type == 'daily' or work_type == 'flexi':
                cal_att_ids = self.env['resource.calendar.attendance'].search([('calendar_id','=',calendar_id)])
                dh = 0
                for cal_att in cal_att_ids:
                    dh += cal_att.sched_hours

            else:
                dh = calendar_obj.get_working_hours_of_date(start_dt=date_from,resource_id=self.employee_id.id)
            leaves = self.count_leaves(date_from, self.employee_id.id, period)
            if not leaves:
                if not dh:
                    dh = 0.00
                duty_hours += dh
            else:
                if leaves[-1] and leaves[-1][-1]:
                    if float(leaves[-1][-1]) == (-0.5):
                        duty_hours += dh / 2
        return duty_hours

    @api.multi
    def get_previous_month_diff(self, employee_id, prev_timesheet_date_from):
        total_diff = 0.0
        timesheet_ids = self.search(
            [('employee_id', '=', employee_id),
             ('date_from', '<', prev_timesheet_date_from)
             ])
        for timesheet in timesheet_ids:
            total_diff += timesheet.get_overtime(
                start_date=prev_timesheet_date_from)
        return total_diff

    @api.multi
    def _get_user_datetime_format(self):
        """ Get user's language & fetch date/time formats of
        that language """
        lang_obj = self.env['res.lang']
        language = self.env.user.lang
        lang_ids = lang_obj.search([('code', '=', language)])
        date_format = _('%Y-%m-%d')
        time_format = _('%H:%M:%S')
        for lang in lang_ids:
            date_format = lang.date_format
            time_format = lang.time_format
        return date_format, time_format

    @api.multi
    def attendance_analysis(self, timesheet_id=None, function_call=False):
        attendance_obj = self.env['hr.attendance']
        date_format, time_format = self._get_user_datetime_format()

        for sheet in self:
            if sheet.id == timesheet_id:
                employee_id = sheet.employee_id.id
                start_date = sheet.date_from
                end_date = sheet.date_to
                previous_month_diff = self.get_previous_month_diff(employee_id, start_date)
                current_month_diff = previous_month_diff
                period = {'date_from': start_date,
                          'date_to': end_date}

                res = {
                    'previous_month_diff': previous_month_diff,
                    'hours': []
                }

                period = {'date_from': start_date,
                          'date_to': end_date
                          }
                dates = list(rrule.rrule(rrule.DAILY,
                                         dtstart=parser.parse(start_date),
                                         until=parser.parse(
                                             end_date)))


                work_current_month_diff = 0.0
                total = {'worked_hours': 0.0, 'duty_hours': 0.0,
                         'diff':current_month_diff, 'work_current_month_diff': '',
                         'auth_ot':0.0, 'actual_ot':0.0, 'actual_worked_hours': 0.0,
                         'core_hours': 0.0, 'core_worked': 0.0}


                for date_line in dates:

                    dh = sheet.calculate_duty_hours(date_from=date_line,
                                                    period=period,
                                                    )
                    leaves = self.count_leaves(date_line, self.employee_id.id, period)
                    worked_hours = 0.0
                    for att in sheet.period_ids:
                        if att.name == date_line.strftime('%Y-%m-%d'):
                            worked_hours = att.total_attendance


                    contract_ids = self.get_contract(employee_id, date_line)
                    for contract in contract_ids:
                        attendance_obj = self.env['hr.attendance']
                        work_type = contract.working_hours.work_type or False

                    diff = worked_hours - dh
                    current_month_diff += diff
                    work_current_month_diff += diff
                    summary_ids = self.env['hr_timesheet.summary'].search([('date', '=', date_line.strftime('%Y-%m-%d')), ('sheet_id', '=', sheet.id)])
                    get_date = date_line.strftime(date_format)
                    get_duty_hours_from_to = self.get_duty_hours_from_to(leaves, employee_id, date_line)
                    get_worked_hours = self.get_worked_hours(employee_id, date_line,get_duty_hours_from_to)
                    get_authorized_ot = self.get_authorized_ot(employee_id, date_line)
                    if sheet.auto_overtime:
                        get_actual_ot = 0
                        for rec in summary_ids:
                            get_actual_ot = rec.actual_ot
                    else:
                        get_actual_ot = self.get_actual_ot(diff,get_authorized_ot, get_worked_hours)
                    if sheet.auto_worked_hours:
                        get_actual_worked_hours = 0
                        for rec in summary_ids:
                            get_actual_worked_hours = rec.actual_worked_hours
                    else:
                        get_actual_worked_hours = get_worked_hours['actual_wh']
                    print 'date_line', date_line
                    get_remarks = self.get_remarks(leaves, diff, get_actual_worked_hours, get_worked_hours, get_actual_ot, dh, worked_hours)
                    get_core_hours = self.get_core_hours(employee_id, date_line)

                    if dh <= 0:
                        disp_dh = ''
                    else:
                        disp_dh = attendance_obj.float_time_convert(dh)
                        # disp_dh = str(round(dh, 2))

                    if worked_hours <=0:
                        disp_worked_hours = ''
                    else:
                        disp_worked_hours = attendance_obj.float_time_convert(worked_hours)
                        # disp_worked_hours = str(round(worked_hours, 2))

                    if diff == 0:
                        disp_diff = ''
                    else:
                        disp_diff = self.sign_float_time_convert(diff)
                        # disp_diff = str(round(diff, 2))

                    if get_authorized_ot['ot_hour'] <= 0:
                        disp_auth_ot_hr = ''
                    else:
                        disp_auth_ot_hr = attendance_obj.float_time_convert(get_authorized_ot['ot_hour'])
                        # disp_auth_ot_hr = str(round(get_authorized_ot['ot_hour'], 2))

                    if get_actual_worked_hours <= 0:
                        disp_actual_wh = ''
                    else:
                        disp_actual_wh = attendance_obj.float_time_convert(get_actual_worked_hours)
                        # disp_actual_wh = str(round(get_actual_worked_hours, 2))

                    if get_actual_ot <= 0 :
                        disp_actual_ot = ''
                    else:
                        disp_actual_ot = attendance_obj.float_time_convert(get_actual_ot)
                        # disp_actual_ot = str(round(get_actual_ot, 2))


                    if get_core_hours['total_core'] > 0:
                        disp_total_core = attendance_obj.float_time_convert(get_core_hours['total_core'])
                    else:
                        disp_total_core = ''

                    if get_worked_hours['core_worked'] > 0:
                        disp_core_worked = attendance_obj.float_time_convert(get_worked_hours['core_worked'])
                        # disp_core_worked = str(round(get_worked_hours['core_worked'], 2))
                    else:
                        disp_core_worked = ''

                    if date_line:
                        print 'dh', dh
                        atndance_summary_obj = self.env['hr_timesheet.summary']
                        res_atndnce_summary = atndance_summary_obj.search([('date', '=', date_line.strftime(date_format)), ('employee_id', '=', employee_id)])
                        args = {'sheet_id':self.id,'date': date_line.strftime(date_format), 'employee_id': employee_id, 'duty_hours': dh,
                                                        'worked_hours': worked_hours,'diff': diff, 'auth_ot': get_authorized_ot['ot_hour'], 'actual_ot': get_actual_ot,
                                                        'actual_worked_hours': get_actual_worked_hours}

                        # if not sheet.auto_import:
                        if work_type == 'daily':
                            if worked_hours > 0:
                                if not res_atndnce_summary:
                                    atndance_summary_obj.create(args)
                                else:
                                    res_atndnce_summary.write(args)
                        else:
                            if not res_atndnce_summary:
                                atndance_summary_obj.create(args)
                            else:
                                res_atndnce_summary.write(args)

                    if function_call:
                        if work_type == 'daily':
                            if worked_hours > 0:
                                res['hours'].append({
                                    _('Date'): get_date,
                                    _('Duty From'): get_duty_hours_from_to['duty_hours_from'],
                                    _('Duty To'): get_duty_hours_from_to['duty_hours_to'],
                                    # _('Duty Hours'):disp_dh,
                                    _('Sched Hours'): disp_dh,
                                    _('Core Hours From'): get_core_hours['core_hours_from'],
                                    _('Core Hours To'): get_core_hours['core_hours_to'],
                                    _('Core Hours'): disp_total_core,
                                    _('Worked From'): get_worked_hours['check_in'],
                                    _('Worked To'): get_worked_hours['check_out'],
                                    _('Worked Hours'): disp_worked_hours,
                                    _('Difference'): disp_diff,
                                    _('Core Worked'): disp_core_worked,
                                    _('OT From'): get_authorized_ot['hour_from'],
                                    _('OT To'): get_authorized_ot['hour_to'],
                                    _('auth_ot_hour'): disp_auth_ot_hr,
                                    _('actual_ot'): disp_actual_ot,
                                    _('actual_wh'): disp_actual_wh,
                                    _('Remarks'): get_remarks,
                                    # _('Running'): self.sign_float_time_convert(
                                    #     current_month_diff)
                                })
                        else:
                            res['hours'].append({
                                _('Date'): get_date,
                                _('Duty From'): get_duty_hours_from_to['duty_hours_from'],
                                _('Duty To'): get_duty_hours_from_to['duty_hours_to'],
                                # _('Duty Hours'):disp_dh,
                                _('Sched Hours'): disp_dh,
                                _('Core Hours From'): get_core_hours['core_hours_from'],
                                _('Core Hours To'): get_core_hours['core_hours_to'],
                                _('Core Hours'): disp_total_core,
                                _('Worked From'):get_worked_hours['check_in'],
                                _('Worked To'):get_worked_hours['check_out'],
                                _('Worked Hours'):disp_worked_hours,
                                _('Difference'):disp_diff,
                                _('Core Worked'): disp_core_worked,
                                _('OT From'): get_authorized_ot['hour_from'],
                                _('OT To'): get_authorized_ot['hour_to'],
                                _('auth_ot_hour'): disp_auth_ot_hr,
                                _('actual_ot'): disp_actual_ot,
                                _('actual_wh'): disp_actual_wh,
                                _('Remarks'): get_remarks,
                                # _('Running'): self.sign_float_time_convert(
                                #     current_month_diff)
                            })

                    else:
                        res['hours'].append({
                            'name': date_line.strftime(date_format),
                            'dh': attendance_obj.float_time_convert(dh),
                            'worked_hours': attendance_obj.float_time_convert(
                                worked_hours),
                            'diff': self.sign_float_time_convert(diff),
                            'running': self.sign_float_time_convert(
                                current_month_diff)})
                    total['duty_hours'] += dh
                    total['worked_hours'] += worked_hours
                    total['diff'] += diff
                    total['work_current_month_diff'] = work_current_month_diff
                    total['core_hours'] += get_core_hours['total_core']
                    total['core_worked'] += get_worked_hours['core_worked']
                    total['auth_ot'] += get_authorized_ot['ot_hour']
                    total['actual_ot'] += get_actual_ot
                    total['actual_worked_hours'] += get_actual_worked_hours
                    res['total'] = total
                return res

    @api.multi
    def get_contract(self, emp_id, date_line):
        contract_obj = self.env['hr.contract']
        contract_ids = contract_obj.search([
            ('employee_id', '=', emp_id),
            ('date_start', '<=', date_line),
            '|',
            ('date_end', '>=', date_line),
            ('date_end', '=', None)
        ])

        return contract_ids

    @api.multi
    def get_duty_hours_from_to(self, leaves, emp_id, date_line):
        contract_obj = self.env['hr.contract']
        contract_ids = self.get_contract(emp_id, date_line)
        if not contract_ids:
            raise ValidationError('No contract created for the assigned employee')
        duty_hours_from = ''
        duty_hours_to = ''
        df_ctr = 0
        dt_ctr = 0

        for contract in contract_ids:
            attendance_obj = self.env['hr.attendance']
            calendar_id = contract.working_hours.id
            work_type = contract.working_hours.work_type
            if work_type == 'daily' or work_type == 'flexi':
                calendar_atndnce_ids = self.env['resource.calendar.attendance'].search(
                    [('calendar_id', '=', calendar_id)])
            else:

                dayweek = date_line.weekday()
                calendar_atndnce_ids = self.env['resource.calendar.attendance'].search(
                    [('calendar_id', '=', calendar_id), ('dayofweek', '=', dayweek)])
            if not leaves:
                for rec in calendar_atndnce_ids:
                    if rec.hour_from:
                        if df_ctr > 0:
                            duty_hours_from = duty_hours_from + '/' + str(
                                attendance_obj.float_time_convert(rec.hour_from))
                        else:
                            duty_hours_from = duty_hours_from + str(
                                attendance_obj.float_time_convert(rec.hour_from))
                        df_ctr += 1
                    if rec.hour_to:
                        if dt_ctr > 0:
                            duty_hours_to = duty_hours_to + '/' + str(
                                attendance_obj.float_time_convert(rec.hour_to))
                        else:
                            duty_hours_to = duty_hours_to + str(attendance_obj.float_time_convert(rec.hour_to))
                        dt_ctr += 1
        vals = {'duty_hours_from': duty_hours_from,
                'duty_hours_to': duty_hours_to,
                'calendar_atndnce_ids': calendar_atndnce_ids,
                }

        return vals

    @api.multi
    def get_core_hours(self, emp_id, date_line):
        contract_obj = self.env['hr.contract']
        contract_ids = self.get_contract(emp_id, date_line)
        if not contract_ids:
            raise ValidationError('No contract created for the assigned employee')
        core_hours_from = ''
        core_hours_to = ''
        cf_ctr = 0
        ct_ctr = 0
        total_core = 0
        for contract in contract_ids:
            attendance_obj = self.env['hr.attendance']
            calendar_id = contract.working_hours.id
            work_type = contract.working_hours.work_type
            if work_type == 'flexi':
                calendar_atndnce_ids = self.env['resource.calendar.attendance'].search(
                    [('calendar_id', '=', calendar_id)])

                for rec in calendar_atndnce_ids:
                    if rec.flex_start:
                        if cf_ctr > 0:
                            core_hours_from = core_hours_from + '/' + str(
                                attendance_obj.float_time_convert(rec.flex_start))
                        else:
                            core_hours_from = core_hours_from + str(
                                attendance_obj.float_time_convert(rec.flex_start))
                        cf_ctr += 1
                    if rec.flex_end:
                        if ct_ctr > 0:
                            core_hours_to = core_hours_to + '/' + str(
                                attendance_obj.float_time_convert(rec.flex_end))
                        else:
                            core_hours_to = core_hours_to + str(attendance_obj.float_time_convert(rec.flex_end))
                        ct_ctr += 1
                    total_core += (rec.flex_end - rec.flex_start)

        vals = {'core_hours_from': core_hours_from,
                'core_hours_to': core_hours_to,
                'total_core': total_core,
                }

        return vals

    @api.multi
    def get_worked_hours(self, employee_id, date_line, duty_hours):
        dtf = DEFAULT_SERVER_DATETIME_FORMAT
        df = '%Y-%m-%d'
        attendance_obj = self.env['hr.attendance']
        rec_ctr = 0
        get_date = date_line.strftime('%Y-%m-%d')
        user_tz = self.env.user.tz or str(pytz.utc)
        local = pytz.timezone(user_tz)
        check_in = ''
        check_out = ''
        ci_ctr = 0
        co_ctr = 0
        diff_out_in = 0
        actual_wh = 0
        core_worked= 0
        get_check_out = ''
        check_out_ttf = 0
        check_out_dte = ''
        res_atndnce = attendance_obj.search([('employee_id', '=', employee_id)], order='check_in asc')
        attendance_ids = res_atndnce.filtered(
            lambda r: r.check_in and datetime.strftime(pytz.utc.localize(datetime.strptime(r.check_in, dtf)).astimezone(local),'%Y-%m-%d') == get_date
                      )#and datetime.strftime(pytz.utc.localize(datetime.strptime(r.check_out, df)).astimezone(local),'%Y-%m-%d') == get_date
        if attendance_ids:
            for rec in attendance_ids:
                get_check_in = datetime.strftime(pytz.utc.localize(datetime.strptime(rec.check_in, dtf)).astimezone(local), "%H:%M")
                check_in_time = datetime.strptime(get_check_in + ':00', "%H:%M:%S") - datetime.strptime('00:00:00',"%H:%M:%S")
                check_in_ttf = seconds(check_in_time) / 3600
                check_in_dte = datetime.strftime(pytz.utc.localize(datetime.strptime(rec.check_in, dtf)).astimezone(local), "%Y-%m-%d")
                if rec.check_out:
                    get_check_out = datetime.strftime(pytz.utc.localize(datetime.strptime(rec.check_out, dtf)).astimezone(local), "%H:%M")
                    check_out_time = datetime.strptime(get_check_out + ':00', "%H:%M:%S") - datetime.strptime('00:00:00', "%H:%M:%S")
                    check_out_ttf = seconds(check_out_time) / 3600
                    check_out_dte = datetime.strftime(pytz.utc.localize(datetime.strptime(rec.check_out, dtf)).astimezone(local), "%Y-%m-%d")

                """ start: work hours from to display"""

                if check_in_dte == check_out_dte or check_in_dte:
                    wh_in = ' ' + get_check_in
                    wh_out  = ' ' + get_check_out
                else:
                    wh_in = '(' + str(datetime.strptime(check_in_dte, df).day) + ')' + ' ' + get_check_in
                    wh_out = '('+ str(datetime.strptime(check_out_dte,df).day) + ')' + ' ' + get_check_out

                if ci_ctr > 0:
                    check_in = check_in + '/' + wh_in
                else:
                    check_in = check_in +  wh_in
                ci_ctr += 1


                if co_ctr > 0:
                    check_out = check_out + '/' + wh_out
                else:
                    check_out = check_out + wh_out
                co_ctr += 1

                print 'ci', check_in
                print 'co', check_out

                """ end: work hours from to display"""

                if len(duty_hours['calendar_atndnce_ids']) > rec_ctr:
                    if duty_hours['calendar_atndnce_ids'][rec_ctr]:
                        for calendar in duty_hours['calendar_atndnce_ids'][rec_ctr]:
                            work_type = calendar.work_type
                            flexi_type = calendar.flexi_type
                            duty_hr_from = attendance_obj.float_time_convert(calendar.hour_from)
                            duty_hr_to = attendance_obj.float_time_convert(calendar.hour_to)
                            flex_start = calendar.flex_start
                            flex_end = calendar.flex_end
                            sched_hours = calendar.sched_hours

                            if work_type == 'weekly' or work_type == 'daily':
                                diff_in = 0
                                diff_out = 0

                                if check_in_dte == check_out_dte:
                                    if (get_check_in >= duty_hr_from):
                                        diff_in = check_in_ttf - calendar.hour_from
                                    if (get_check_out <= duty_hr_to):
                                        diff_out = calendar.hour_to -  check_out_ttf
                                # else:
                                #     if (get_check_in >= duty_hr_from):
                                #         diff_in = check_in_ttf - calendar.hour_from
                                    diff = diff_in + diff_out
                                    diff_out_in = sched_hours - diff

                            elif flexi_type == 'range':
                                if get_check_in >= duty_hr_from:
                                    if get_check_out <= duty_hr_to:
                                        diff_out_in = check_out_ttf - check_in_ttf
                                    if get_check_out > duty_hr_to:
                                        diff_out_in = calendar.hour_to - check_in_ttf

                                if get_check_in < duty_hr_from:
                                    if get_check_out <= duty_hr_to:
                                        diff_out_in = check_out_ttf - duty_hr_from
                                    if get_check_out > duty_hr_to:
                                        diff_out_in = calendar.hour_to - duty_hr_from

                            elif flexi_type == 'band' or flexi_type == 'core' or flexi_type == 'core_plus':
                                core_hours = flex_end - flex_start
                                if get_check_in <= duty_hr_from and get_check_out >= duty_hr_to:
                                    get_wh = check_out_ttf - check_in_ttf
                                    diff_out_in = sched_hours
                                elif get_check_in <= duty_hr_from and get_check_out < duty_hr_to:
                                    get_wh = check_out_ttf - calendar.hour_from
                                    if check_out_ttf >= flex_end:
                                        core_worked = flex_end - flex_start
                                    elif check_in_ttf < flex_end:
                                        core_worked = check_out_ttf - flex_start
                                elif get_check_in > duty_hr_from and get_check_out >= duty_hr_to:
                                    get_wh = calendar.hour_to - check_in_ttf
                                    if check_in_ttf <= flex_start:
                                        core_worked = flex_end - flex_start
                                    elif check_in_ttf > flex_start:
                                        core_worked = flex_end - check_in_ttf

                                elif get_check_in > duty_hr_from and get_check_out < duty_hr_to:
                                    get_wh = check_out_ttf - check_in_ttf
                                    if check_in_ttf <= flex_start and check_out_ttf >= flex_end:
                                        core_worked = flex_end - flex_start
                                    elif check_in_ttf <=flex_start and check_out_ttf < flex_end:
                                        core_worked = check_out_ttf - flex_start
                                    elif check_in_ttf > flex_start and check_out_ttf > flex_end:
                                        core_worked = flex_end - check_in_ttf
                                    elif check_in_ttf > flex_start and check_out_ttf < flex_end:
                                        core_worked = check_out_ttf - check_in_ttf

                                else:
                                    get_wh = check_out_ttf - check_in_ttf
                                    core_worked = get_wh

                                if core_worked < core_hours:
                                    diff_out_in = core_worked
                                else:
                                    diff_out_in = get_wh

                            if diff_out_in >= sched_hours:
                                diff_out_in = sched_hours


                        actual_wh = actual_wh + diff_out_in
                rec_ctr += 1


        # else:
        #         if ci_ctr > 0:
        #             check_in = check_in + '/' + 'NO CI'
        #         else:
        #             check_in = check_in + 'NO CI'
        #         ci_ctr += 1
        #
        #         if co_ctr > 0:
        #             check_out = check_out + '/' + 'NO CO'
        #         else:
        #             check_out = check_out + 'NO CO'
        #         co_ctr += 1

                # rec_ctr += 1

        # actual_wh = diff_out_in

        vals = {'check_in': check_in,
                'check_out': check_out,
                'attendance_ids': attendance_ids,
                'actual_wh': actual_wh,
                'core_worked': core_worked,
                }


        return vals

    # @api.multi
    # def get_actual_worked_hours(self, diff, worked_hours, dh, get_duty_hours_from_to, employee_id, date_line):
    #     if diff > 0:
    #         actual_wh = dh
    #     else:
    #         actual_wh = worked_hours
    #
    #     return actual_wh



    @api.multi
    def get_authorized_ot(self, employee_id, date_line):
        attendance_obj = self.env['hr.attendance']
        get_date = date_line.strftime('%Y-%m-%d')

        hour_from = ''
        hour_to = ''
        hf_ctr = 0
        ht_ctr = 0
        ot_hour = 0
        overtime_det_ids = []

        res_ot = self.env['hr.overtime'].search([('start_date', '<=', get_date), ('end_date', '>=', get_date),('state','=','approve')], order = 'start_date asc')
        for rec_ot in res_ot:
            self.env.cr.execute( """SELECT overtime_id, employee_id from overtime_employee_rel where overtime_id = %s and employee_id = %s""",(rec_ot.id, employee_id))
            res =  self.env.cr.fetchall()
            if rec_ot.employee_id.id == employee_id or res:
                res_ot_det = self.env['hr.overtime.det'].search([('overtime_id', '=', rec_ot.id)], order = 'start_time asc')
                start_date = rec_ot.start_date
                end_date = rec_ot.end_date
                for ot_det in res_ot_det:
                    if get_date >= start_date and get_date <= end_date:
                        get_hour_from = ot_det.start_time
                        if get_hour_from:
                            if hf_ctr > 0:
                                hour_from = hour_from + '/' + attendance_obj.float_time_convert(get_hour_from)
                            else:
                                hour_from = hour_from + attendance_obj.float_time_convert(get_hour_from)

                        hf_ctr += 1
                        get_hour_to = ot_det.end_time
                        if get_hour_to:
                            if ht_ctr > 0:
                                hour_to = hour_to + '/' + attendance_obj.float_time_convert(get_hour_to)
                            else:
                                hour_to = hour_to + attendance_obj.float_time_convert(get_hour_to)
                        ht_ctr += 1

                        ot_hour = ot_hour + ot_det.numofhours
                        overtime_det_ids.append(ot_det.id)

        vals = {'hour_from': hour_from,
                'hour_to': hour_to,
                'ot_hour': ot_hour,
                'overtime_det_ids': overtime_det_ids}
        return vals

    @api.multi
    def get_actual_ot(self, diff, get_authorized_ot, get_worked_hours):
        attendance_obj = self.env['hr.attendance']
        user_tz = self.env.user.tz or str(pytz.utc)
        local = pytz.timezone(user_tz)
        get_ot = 0
        attendance_ids = get_worked_hours['attendance_ids']
        overtime_det_ids =  get_authorized_ot['overtime_det_ids']
        for overtime in overtime_det_ids:
            ot_id = self.env['hr.overtime.det'].browse(overtime)
            print 'ot_start', ot_id.overtime_id.start_date
            ftt_start_time = attendance_obj.float_time_convert(ot_id.start_time)
            get_start_time = datetime.strptime(ftt_start_time + ':00', "%H:%M:%S")
            ot_start_time = datetime.strftime(get_start_time , "%H:%M:%S")
            ftt_end_time = attendance_obj.float_time_convert(ot_id.end_time)
            get_end_time = datetime.strptime(ftt_end_time + ':00', "%H:%M:%S")
            ot_end_time = datetime.strftime(get_end_time , "%H:%M:%S")
            for attendance in attendance_ids:
                atndnce_id = attendance_obj.browse(attendance.id)
                check_in = datetime.strftime(pytz.utc.localize(datetime.strptime(atndnce_id.check_in, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%H:%M:%S")
                check_out = datetime.strftime(pytz.utc.localize(datetime.strptime(atndnce_id.check_out, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%H:%M:%S")
                check_in_dte = datetime.strftime(pytz.utc.localize(datetime.strptime(atndnce_id.check_in, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%Y-%m-%d")
                check_out_dte = datetime.strftime(pytz.utc.localize(datetime.strptime(atndnce_id.check_out, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%Y-%m-%d")

                if check_in_dte == check_out_dte:
                    if ot_start_time >= check_in and ot_start_time<= check_out:
                        if ot_end_time >= check_out:
                            if check_out >= ot_start_time:
                                diff = datetime.strptime(check_out, "%H:%M:%S") - datetime.strptime(ot_start_time, "%H:%M:%S")
                                get_ot = get_ot + seconds(diff) / 3600.0
                        else:
                            if ot_end_time >= ot_start_time:
                                diff = datetime.strptime(ot_end_time, "%H:%M:%S") - datetime.strptime(ot_start_time, "%H:%M:%S")
                                get_ot = get_ot + seconds(diff) / 3600.0
                    elif ot_start_time < check_in and ot_start_time <= check_out:
                        if ot_end_time >= check_out:
                            if check_out > check_in:
                                diff = datetime.strptime(check_out, "%H:%M:%S") - datetime.strptime(check_in, "%H:%M:%S")
                                get_ot = get_ot + seconds(diff) / 3600.0
                        else:
                            if ot_end_time >= check_in:
                                diff = datetime.strptime(ot_end_time, "%H:%M:%S") - datetime.strptime(check_in, "%H:%M:%S")
                                get_ot = get_ot + seconds(diff) / 3600.0
                else:
                    if ot_start_time >= check_in:
                        diff = datetime.strptime(ot_end_time, "%H:%M:%S") - datetime.strptime(ot_start_time, "%H:%M:%S")
                        get_ot = get_ot + seconds(diff) / 3600.0
                    else:
                        diff = datetime.strptime(ot_end_time, "%H:%M:%S") - datetime.strptime(check_in, "%H:%M:%S")
                        get_ot = get_ot + seconds(diff) / 3600.0


                # if ot_start_time < check_in and ot_start_time<= check_out:
                #     if ot_end_time >= check_out:
                #         diff = datetime.strptime(check_out, "%H:%M:%S") - datetime.strptime(check_in,
                #                                                                             "%H:%M:%S")
                #         get_ot = get_ot + seconds(diff) / 3600.0
                #     else:
                #         diff = datetime.strptime(ot_end_time, "%H:%M:%S") - datetime.strptime(check_in,
                #                                                                               "%H:%M:%S")
                #         get_ot = get_ot + seconds(diff) / 3600.0

                # if ot_start_time <= check_in and ot_end_time>= check_out:
                #     diff = datetime.strptime(check_out, "%H:%M:%S") - datetime.strptime(check_in, "%H:%M:%S")
                #     get_ot = get_ot + seconds(diff) / 3600

        return get_ot


    @api.multi
    def get_remarks(self, leaves, diff, actual_wh, get_wh, get_actual_ot, dh, wh):
        attendance_ids =  get_wh['attendance_ids']
        remark = ''

        if wh > 0:
            if diff < 0:
                remark = 'UT'
            elif diff >= 0:
                if get_actual_ot > 0:
                    remark = 'OT'
                elif actual_wh < dh:
                    remark = 'UT'

        elif leaves:
            remark = 'LEA'

        elif dh <= 0:
            remark = ''

        elif attendance_ids:
            if attendance_ids.check_in and not attendance_ids.check_out:
                remark = 'NO CO'
            elif not attendance_ids.check_in and attendance_ids.check_out:
                remark = 'NO CI'
        else:
            remark = 'ABS'
        return remark

    @api.multi
    def sign_float_time_convert(self, float_time):
        sign = '-' if float_time < 0 else ''
        attendance_obj = self.env['hr.attendance']
        return sign + attendance_obj.float_time_convert(float_time)

    @api.multi
    def write(self, vals):
        if 'state' in vals and vals['state'] == 'done':
            vals['total_diff_hours'] = self.calculate_diff(None)
            for sheet in self:
                vals['total_duty_hours_done'] = sheet.total_duty_hours
        elif 'state' in vals and vals['state'] == 'draft':
            vals['total_diff_hours'] = 0.0
        res = super(HrTimesheetSheet, self).write(vals)
        return res

    @api.multi
    def calculate_diff(self, end_date=None):
        for sheet in self:
            return sheet.total_duty_hours * (-1)



def seconds(td):
    assert isinstance(td, timedelta)
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10.**6