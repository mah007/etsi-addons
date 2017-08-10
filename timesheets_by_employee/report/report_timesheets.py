# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2009-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import pytz

from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ReportTimesheet(models.AbstractModel):
    _name = 'report.timesheets_by_employee.report_timesheets'

    def get_timesheets(self, docs):
        """input : name of employee and the starting date and ending date
        output: timesheets by that particular employee within that period and the total duration"""

        if docs.from_date and docs.to_date:
            rec = self.env['account.analytic.line'].search([('user_id', '=', docs.employee[0].id),
                                                        ('date', '>=', docs.from_date),('date', '<=', docs.to_date)])

            emp_id = self.env['hr.employee'].search([('user_id','=',docs.employee[0].id)])

            timesheet_sum = self.env['hr_timesheet.summary'].search([('employee_id','=',emp_id.id),
                                                            ('date', '>=', docs.from_date),
                                                            ('date', '<=', docs.to_date)],order='date ASC')

            if timesheet_sum:
                attendance = self.env['hr.attendance'].search([('employee_id','=',emp_id.id)
                                                            ,('sheet_id', '=', timesheet_sum[0].sheet_id.id)],
                                                              order='check_in ASC')
            # attendance1 = self.env['hr.attendance'].search(
            #     [('employee_id', '=', emp_id.id), ('sheet_id', 'in', timesheet_sum.sheet_id.id)])

        elif docs.from_date:
            rec = self.env['account.analytic.line'].search([('user_id', '=', docs.employee[0].id),
                                                        ('date', '>=', docs.from_date)])
        elif docs.to_date:
            rec = self.env['account.analytic.line'].search([('user_id', '=', docs.employee[0].id),
                                                            ('date', '<=', docs.to_date)])
        else:
            rec = self.env['account.analytic.line'].search([('user_id', '=', docs.employee[0].id)])
        records = []
        analysis = []
        total = 0
        for r in rec:
            vals = {'project': r.project_id.name,
                    'user': r.user_id.partner_id.name,
                    'duration': r.unit_amount,
                    'date': r.date,
                    }
            total += r.unit_amount
            records.append(vals)

        for rec in timesheet_sum:

            restday = False
            for res in attendance:
                # attn = self.env['hr.attendance'].browse(rec.sheet_id.id)
                # attn = attendance.search('sheet_id','=',rec.sheet_id.id)
                # print 'attn', attn
                df = DEFAULT_SERVER_DATETIME_FORMAT
                user_tz = self.env.user.tz or str(pytz.utc)
                local = pytz.timezone(user_tz)

                check_in = datetime.strftime(
                    pytz.utc.localize(datetime.strptime(res.check_in, df)).astimezone(local),
                    "%Y-%m-%d %H:%M:%S")
                check_out = datetime.strftime(
                    pytz.utc.localize(datetime.strptime(res.check_out, df)).astimezone(local),
                    "%Y-%m-%d %H:%M:%S")
                # off_date = datetime.strftime(
                #     pytz.utc.localize(datetime.strptime(rec.date, df)).astimezone(local),
                #     "%Y-%m-%d")

                official_date = datetime.strptime(rec.date, "%Y-%m-%d").date()
                check_in_date = datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S").date()
                check_out_date = datetime.strptime(check_out, "%Y-%m-%d %H:%M:%S").date()
                check_in_time = datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S").time()
                check_out_time = datetime.strptime(check_out, "%Y-%m-%d %H:%M:%S").time()

                _time_in =  check_in_time.strftime("%H:%M")
                _time_out = check_out_time.strftime("%H:%M")
                _off_date = official_date.strftime("%m-%d-%Y")

                if official_date == check_in_date:
                    print 'DATE', rec.date
                    val = {'employee': rec.employee_id.name,
                            # 'date': rec.date,
                            'date': _off_date,
                            'check_in': _time_in,
                            'check_out': _time_out,
                            'duty_hours': rec.duty_hours,
                            'worked_hours': rec.worked_hours,
                            'actual_worked_hours': rec.actual_worked_hours,
                            'auth_ot':rec.auth_ot,
                            'actual_ot': rec.actual_ot,
                            'diff':rec.diff,
                            }
                    restday = True
                    print '>>>',restday
                    analysis.append(val)
            if restday == False:
                print 'DATE', rec.date
                val = {'employee': rec.employee_id.name,
                       # 'date': rec.date,
                       'date': _off_date,
                       'check_in': '',
                       'check_out': '',
                       'duty_hours': rec.duty_hours,
                       'worked_hours': rec.worked_hours,
                       'actual_worked_hours': rec.actual_worked_hours,
                       'auth_ot': rec.auth_ot,
                       'actual_ot': rec.actual_ot,
                       'diff': rec.diff,
                       }
                print '>>>', restday
                analysis.append(val)

        print 'analysis', analysis
        emp = self.env['hr.employee'].search([('user_id', '=', docs.employee[0].id)])
        return [records, total, analysis, emp]

    @api.model
    def render_html(self, docids, data=None):
        """we are overwriting this function because we need to show values from other models in the report
        we pass the objects in the docargs dictionary"""

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        identification = []
        for i in self.env['hr.employee'].search([('user_id', '=', docs.employee[0].id)]):
            if i:
                identification.append({'id': i.identification_id, 'name': i.name_related})

        timesheets = self.get_timesheets(docs)

        sum_duty_hrs = 0; sum_act_ot =0; sum_act_worked = 0; sum_auth_ot=0

        for i in timesheets[2]:
            sum_duty_hrs += i['duty_hours']
            sum_act_worked += i['actual_worked_hours']
            sum_auth_ot += i['auth_ot']
            sum_act_ot += i['actual_ot']

        period = None
        if docs.from_date and docs.to_date:
            period = "From " + str(docs.from_date) + " To " + str(docs.to_date)
        elif docs.from_date:
            period = "From " + str(docs.from_date)
        elif docs.from_date:
            period = " To " + str(docs.to_date)

        _from_date = datetime.strptime(docs.from_date,"%Y-%m-%d").date()
        _to_date = datetime.strptime(docs.to_date, "%Y-%m-%d").date()

        __from_date = _from_date.strftime("%m-%d-%Y")
        __to_date = _to_date.strftime("%m-%d-%Y")

        docargs = {
           'doc_ids': self.ids,
           'doc_model': self.model,
           'docs': docs,
           'timesheets': timesheets[0],
           'total': timesheets[1],
           'company': docs.employee[0].company_id.name,
            'from_date': __from_date,
            'to_date': __to_date,
           # 'manager_name': docs.employee[0].parent_id.name,
           'identification': identification,
           'period': period,
           'timesheet_analysis':timesheets[2],
           'timesheet_emp': timesheets[3],
           'sum_duty': sum_duty_hrs,
           'sum_worked': sum_act_worked,
           'sum_ot': sum_act_ot,
           'sum_auth_ot': sum_auth_ot,
        }

        print 'docargs', docargs
        return self.env['report'].render('timesheets_by_employee.report_timesheets', docargs)
