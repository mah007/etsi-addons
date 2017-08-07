import pytz

from odoo import api, fields, models, tools, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import time
import dateutil.parser
from dateutil import relativedelta
import babel
from odoo.exceptions import UserError, ValidationError

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

def _compute_basic_salary(self,worked_days):
    sal = self.wage
    s_pay_type = self.payroll_type
    s_sched_pay = self.schedule_pay

    if s_pay_type == 'daily':
        if s_sched_pay == 'weekly':
            if worked_days:
                basic = worked_days.ATTN.number_of_days * sal
        elif s_sched_pay == 'monthly':
            basic = sal * 30
        elif s_sched_pay == 'semi-monthly':
            basic = sal * 15
            # basic = worked_days.WORK100.number_of_days * sal
    else:
        if s_sched_pay == 'monthly':
            basic = sal
        elif s_sched_pay == 'semi-monthly':
            basic = sal / 2

    return round(basic, 2)

def _get_rate(self, code):
    working_days = self.env['resource.calendar.attendance'].search([('calendar_id','=',self.working_hours.id)])
    hrs_week = 0
    for rec in working_days:
        hrs_week += rec.sched_hours

    if self.working_hours.work_type == 'weekly':
        if hrs_week == 48:
            working_days_year = 313.00
        elif hrs_week == 40:
            working_days_year = 261.00
    elif self.working_hours.work_type == 'flexi':
        hrs_week = working_days.flex_week_hours
        if hrs_week == 48:
            working_days_year = 313.00
        elif hrs_week == 40:
            working_days_year = 261.00

    else:
        working_days_year = 365.00

    number_mos = 12
    hours_per_day = 8.00

    if self.payroll_type == 'daily':
        if code == 'hrs':
            rate = (self.wage/ hours_per_day)
        elif code == 'daily':
            rate = self.wage
    elif self.payroll_type == 'monthly':
        if code == 'hrs':
            # rate = (self.wage * number_mos) / working_days_year / hours_per_day
            rate = (self.wage / round((working_days_year / number_mos))) / hours_per_day
        elif code == 'daily':
            rate = self.wage / round((working_days_year / number_mos))
            # _rate = (self.wage * number_mos) / working_days_year

    return rate

def _create_overtime_breakdown(self,ot, rec, policy_lines, amount):
    if not self.env['hr.overtime.breakdown'].search([('worked_days_id','=',ot.id),
                                                     ('type','=',policy_lines.type),
                                                     ('date','=',rec.date)]):
        ot.overtime_breakdown_ids.create({
            'worked_days_id': ot.id,
            'date': rec.date,
            'auth_ot': rec.auth_ot,
            'act_ot': rec.actual_ot,
            'type': policy_lines.type,
            'rate': policy_lines.rate,
            'amount': amount,
            'code': ot.code})

def _create_absence_breakdown(self,attn, rec, leave, absence_line, amount, remark):
    print '>>>',leave
    print '>>>', absence_line
    print '>>>', rec
    if leave:
        if not self.env['hr.absence.breakdown'].search([('worked_days_id', '=', attn.id),
                                                         ('type', '=', absence_line.type),
                                                         ('date', '=', rec.date)]):

            attn.absence_breakdown_ids.create({
                'worked_days_id': attn.id,
                'date': rec.date,
                'duty_hours':rec.duty_hours,
                'auth_abs': abs(leave.number_of_days),
                'act_abs': rec.actual_worked_hours,
                'leave_id': leave.holiday_status_id.id,
                'type': absence_line.type,
                'rate': absence_line.rate,
                'amount': amount,
                'remark':remark})

    else:
        print '>>>>', absence_line[0]
        print '>>>>', absence_line[1]
        if not self.env['hr.absence.breakdown'].search([('worked_days_id', '=', attn.id),
                                                        ('date', '=', rec.date)]):
            attn.absence_breakdown_ids.create({
                'worked_days_id': attn.id,
                'date': rec.date,
                'duty_hours': rec.duty_hours,
                'leave_id': leave.id,
                'auth_abs': 0.00,
                'act_abs': rec.actual_worked_hours,
                'type': absence_line[0],
                'rate': absence_line[1],
                'amount': amount,
                'remark':remark})

def _compute_contri_sss(self, worked_days, freq, model, gross):
    share = self.env[model].search(
        [('sal_range_min', '<=', gross), ('sal_range_max', '>=', gross)])
    return share.employee_share

def _compute_contri(self,worked_days,freq,model):
    # payroll.sss.matrix'
    sal = self.wage
    if self.schedule_pay == 'monthly':
        fr = 1
    elif self.schedule_pay == 'semi-monthly':
        fr = 2
    elif self.schedule_pay == 'weekly':
        fr = 4
    if worked_days:
        # FOR EMPLOYEE SHARE
        if self.payroll_type == 'daily':
            basic = _compute_basic_salary(self, worked_days)
            sal = basic * fr
            contri_id = self.env[model].search(
                [('sal_range_min', '<=', sal), ('sal_range_max', '>=', sal)])
        else:
            contri_id = self.env[model].search(
                [('sal_range_min', '<=', sal), ('sal_range_max', '>=', sal)])

        share = contri_id.employee_share / freq
    else:
        # FOR EMPLOYER SHARE
        if self.payroll_type == 'daily':
            basic = _compute_basic_salary(self, '')
            sal = basic * fr
            contri_id = self.env[model].search(
                [('sal_range_min', '<=', sal), ('sal_range_max', '>=', sal)])

        else:
            contri_id = self.env[model].search(
                [('sal_range_min', '<=', sal), ('sal_range_max', '>=', sal)])

        if model == 'payroll.sss.matrix':
            share = (contri_id.employer_share + contri_id.employer_compensation) / freq
        elif model == 'payroll.philhealth.matrix':
            share = contri_id.employer_share / freq
        elif model == 'payroll.pagibig.matrix':
            share = contri_id.employer_share / freq
    return share

def _determine_pay(company,payslip,self,worked_days,freq,model):
    date_from = datetime.strptime(payslip.date_from, "%Y-%m-%d").date()
    vale_1 = False
    vale_2 = False
    if date_from.day >= 1 and date_from.day <= 15:
        vale_1 = True
        vale_2 = False
    else:
        vale_2 = True
        vale_1 = False

    if company.value == 'first':
        if vale_1:
            emp_share = _compute_contri(self, worked_days, freq, model)
        else:
            emp_share = 0.00
    elif company.value == 'second':
        if vale_2:
            emp_share = _compute_contri(self, worked_days, freq, model)
        else:
            emp_share = 0.00

    return emp_share

def _check_timesheet(self,id):
        timesheet = self.env['hr_timesheet_sheet.sheet'].search([('id', '=', id)])
        if timesheet.auto_import:
            ts = True
        else:
            ts = False
        return ts

def _get_work_days(self, payslip, work_days, code):
    for rec in work_days:
        vals = self.env['hr.payslip.worked_days'].search([('code', '=', code),
                                                             ('contract_id', '=', self.id),
                                                             ('payslip_id', '=', payslip.id)])
    return vals

class Hr_Contract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    sss_contri = fields.Boolean(string='SSS', default = True)
    philhealth_contri = fields.Boolean(string="Philhealth", default = True)
    pagibig_contri = fields.Boolean(string="Pagibig", default = True)
    wtax_contri = fields.Boolean(string="Withholding Tax", default = True)
    # schedule_pay = fields.Selection(selection_add=[('semi-monthly', 'Semi-Monthly')])
    payroll_type = fields.Selection([('daily', 'Daily'), ('monthly', 'Monthly')], string="Payroll Type")
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('semi-monthly', 'Semi-Monthly'),
    ], string='Scheduled Pay', index=True, default='monthly')



    def _get_basic(self,worked_days):
        sal = self.wage
        s_pay_type = self.payroll_type
        s_sched_pay = self.schedule_pay
        basic = 0.00

        if s_pay_type == 'daily':
            if s_sched_pay=='weekly':
                basic = worked_days.ATTN.number_of_days * sal
            elif s_sched_pay == 'monthly':
                basic = sal * 30
            elif s_sched_pay == 'semi-monthly':
                basic = sal * 15
            # basic = worked_days.WORK100.number_of_days * sal
        else:
            if s_sched_pay == 'monthly':
                basic = sal
            elif s_sched_pay == 'semi-monthly':
                basic = sal/2
        return round(basic, 2)

    def _get_sss_contribution(self,worked_days,payslip,categ):
        print 'categ', categ.GROSS
        gross = categ.GROSS
        model = 'payroll.sss.matrix'
        if self.sss_contri:
            if worked_days.ATTN.number_of_days==0.00:
                emp_share = 0.00
            else:
                company = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
                if company.sss_contri:
                    if company.schedule_pay == 'monthly':
                        freq = 2
                        if self.schedule_pay == 'monthly':
                            freq = 1
                        # emp_share = _compute_contri(self, worked_days, freq, model)
                        emp_share = _compute_contri_sss(self, worked_days, freq, model,gross)

                    elif company.schedule_pay == 'semi-monthly':
                        freq=1
                        emp_share = _determine_pay(company, payslip, self, worked_days, freq, model)
                        # emp_shr = _compute_contri_sss(self, worked_days, freq, model, gross)
                    elif company.schedule_pay == 'weekly':
                        freq = 4
                        emp_share = _compute_contri(self, worked_days, freq,model)

        else:
            emp_share = 0.00

        return round(emp_share, 2)

    def _get_philhealth_contribution(self,worked_days,payslip,categ):
        model = 'payroll.philhealth.matrix'
        if self.philhealth_contri:
            if worked_days.ATTN.number_of_days==0.00:
                emp_share = 0.00
            else:
                company = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
                if company.philhealth_contri:
                    if company.schedule_pay == 'monthly':
                        freq = 2
                        if self.schedule_pay == 'monthly':
                            freq = 1
                        emp_share = _compute_contri(self, worked_days, freq, model)
                    elif company.schedule_pay == 'semi-monthly':
                        freq=1
                        emp_share = _determine_pay(company, payslip, self, worked_days, freq, model)

                    elif company.schedule_pay == 'weekly':
                        freq = 4
                        emp_share = _compute_contri(self, worked_days, freq, model)

        else:
            emp_share = 0.00

        return round(emp_share, 2)
        # if self.philhealth_contri:
        #     if worked_days.ATTN.number_of_days == 0.00:
        #         emp_share = 0.00
        #     else:
        #         sched_pay = self.schedule_pay
        #         s_pay_type = self.payroll_type
        #         freq = 1
        #         sal = self.wage
        #
        #         if sched_pay == 'monthly':
        #             freq = 1
        #         elif sched_pay == 'semi-monthly':
        #             freq = 2
        #         elif sched_pay == 'weekly':
        #             freq = 4
        #         else:
        #             sal = self.wage
        #             freq = 1
        #
        #
        #         if s_pay_type == 'daily':
        #             if s_pay_type == 'daily':
        #                 basic = _compute_basic_salary(self,worked_days)
        #                 sal = basic * freq
        #             philhealth_id = self.env['payroll.philhealth.matrix'].search(
        #                 [('sal_range_min', '<=', sal), ('sal_range_max', '>=', sal)])
        #         else:
        #
        #             philhealth_id = self.env['payroll.philhealth.matrix'].search(
        #                 [('sal_range_min', '<=', sal), ('sal_range_max', '>=', sal)])
        #
        #         emp_share = philhealth_id.employee_share / freq
        # else:
        #         emp_share = 0.00
        # return round(emp_share, 2)

    def _get_pagibig_contribution(self,worked_days,payslip,categ):
        model = 'payroll.pagibig.matrix'
        if self.pagibig_contri:
            if worked_days.ATTN.number_of_days == 0.00:
                emp_share = 0.00
            else:
                company = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
                if company.pagibig_contri:
                    if company.schedule_pay == 'monthly':
                        freq = 2
                        if self.schedule_pay == 'monthly':
                            freq = 1
                        emp_share = _compute_contri(self, worked_days, freq, model)
                    elif company.schedule_pay == 'semi-monthly':
                        freq = 1
                        emp_share = _determine_pay(company, payslip, self, worked_days, freq, model)

                    elif company.schedule_pay == 'weekly':
                        freq = 4
                        emp_share = _compute_contri(self, worked_days, freq, model)

        else:
            emp_share = 0.00

        return round(emp_share, 2)
        # if self.pagibig_contri:
        #     if worked_days.ATTN.number_of_days == 0.00:
        #         emp_share = 0.00
        #     else:
        #         sched_pay = self.schedule_pay
        #         s_pay_type = self.payroll_type
        #         freq = 0
        #         sal = self.wage
        #
        #         if sched_pay == 'monthly':
        #             sal = self.wage
        #             freq = 1
        #         elif sched_pay == 'semi-monthly':
        #             freq = 2
        #         elif sched_pay == 'weekly':
        #             freq = 4
        #         else:
        #             sal = self.wage
        #             freq = 1
        #
        #         if s_pay_type == 'daily':
        #             basic = _compute_basic_salary(self,worked_days)
        #             sal = basic * freq
        #             pagibig_id = self.env['payroll.pagibig.matrix'].search(
        #                 [('sal_range_min', '<=', sal), ('sal_range_max', '>=', sal)])
        #         else:
        #             pagibig_id = self.env['payroll.pagibig.matrix'].search(
        #                 [('sal_range_min', '<=', sal), ('sal_range_max', '>=', sal)])
        #
        #         emp_share = pagibig_id.employee_share / freq
        # else:
        #     emp_share = 0.00
        #
        # return round(emp_share, 2)

    def _get_tax(self,gross,deductions,worked_days):
        if self.wtax_contri:
            if worked_days.ATTN.number_of_days == 0:
                wtax = 0.00
            else:
                sched_pay = self.schedule_pay

                selected_emp = self.employee_id.id
                emp_id = self.env['hr.employee'].search([('id', '=', selected_emp)])
                status_id = emp_id.tin_type

                taxable_income = gross - deductions

                if sched_pay == 'monthly':
                    per_ids = self.env['payroll.tax.period'].search([('period_code','=','W')])
                    wtax = self._get_wtax(per_ids, status_id, taxable_income)
                elif sched_pay == 'semi-monthly':
                    per_ids = self.env['payroll.tax.period'].search([('period_code', '=', 'SM')])
                    wtax = self._get_wtax(per_ids,status_id,taxable_income)
                    print 'wtax', wtax
                elif sched_pay == 'weekly':
                    per_ids = self.env['payroll.tax.period'].search([('period_code', '=', 'M')])
                    wtax = self._get_wtax(per_ids, status_id, taxable_income)
        else:
            wtax = 0.00

        return round(wtax, 2)

    def _get_wtax(self,per_ids,status_id,taxable_income):
        exemption_ids = self.env['payroll.tax.exemption'].search([('period_ids', '=', per_ids.id)])
        range_ids=[]

        for rec in exemption_ids:
            id = self.env['payroll.tax.income.range'].search([('exemp_ids', '=', rec.id),
                                                              ('period_ids', '=', per_ids.id),
                                                              ('stat_ids','=',status_id.id)])
            range_ids.append(id)


        for rec in range_ids:
            if taxable_income >= rec.income_min and  taxable_income <= rec.income_max:
                range = rec.income_min
                rate = rec.exemp_ids.tax_rate
                exemption = rec.exemp_ids.tax_value

                tax = exemption + ((taxable_income-range)*rate)

        return round(tax,2)

    def _get_absent(self,payslip):

        work_days = payslip.worked_days_line_ids

        # for rec in work_days:
        #     work100 = self.env['hr.payslip.worked_days'].search([('code', '=', 'WORK100'),
        #                                                     ('contract_id', '=', self.id),
        #                                                     ('payslip_id', '=', payslip.id)])
        #     attn = self.env['hr.payslip.worked_days'].search([('code', '=', 'ATTN'),
        #                                                          ('contract_id', '=', self.id),
        #                                                          ('payslip_id', '=', payslip.id)])

        work100 =_get_work_days(self,payslip,work_days,'WORK100')
        attn =_get_work_days(self,payslip,work_days,'ATTN')

        print 'work100', work100
        print 'attn', attn

        work_hrs = 8
        s_pay_type = self.payroll_type
        sal = self.wage
        duty_days = work100.number_of_days
        actual_days = attn.number_of_days
        duty_hrs = work100.number_of_hours
        actual_hrs =attn.number_of_hours
        abs_hrs = duty_hrs - actual_hrs
        abs_days = duty_days - actual_days
        # hourly_rate = _get_rate('hrs', sal)
        # daily_rate = _get_rate('daily', sal)

        hourly_rate = _get_rate(self,'hrs')
        daily_rate = _get_rate(self,'daily')

        absent_pay = 0.00
        paid = 0.00
        unpaid = 0.00
        dock = 0.00
        absent = 0.00
        undertime = 0.00
        late_pay = 0.00
        late = 0.00
        holi = 0.00

        if actual_hrs == 0:
            absent_pay = self._get_basic('')
        else:

            if self.policy_id.id:
                policy_group_id = self.policy_id.id
                print policy_group_id
                self.env.cr.execute(
                    "SELECT group_id, absence_id from hr_policy_group_absence_rel where group_id = \'%s\'" % policy_group_id)
                res = self.env.cr.fetchall()
                print 'recs>>>', res

                p_list = []
                for r in res:
                    print r[1]
                    p_list.append(r[1])
                print 'pList', p_list


                if self.working_hours.work_type != 'flexi':
                # if self.working_hours.work_type:


                    timesheet_sum = self.env['hr_timesheet.summary'].search([('employee_id', '=', self.employee_id.id),
                                                                             ('duty_hours', '!=', 0.00),
                                                                             ('actual_worked_hours', '<', 8.00),
                                                                             # ('diff', '<', 0.00),
                                                                             ('date', '>=', payslip.date_from),
                                                                             ('date', '<=', payslip.date_to)])

                    timesheet_sum_leave = self.env['hr_timesheet.summary'].search([('employee_id', '=', self.employee_id.id),
                                                                             ('duty_hours', '=', 0.00),
                                                                             ('date', '>=', payslip.date_from),
                                                                             ('date', '<=', payslip.date_to)])

                    for rec in timesheet_sum_leave:
                        print rec.date
                        leave = self.env['hr.holidays'].search([('date_from', '<=', rec.date),
                                                                ('date_to', '>=', rec.date),
                                                                ('employee_id', '=', self.employee_id.id),
                                                                ('state', '=', 'validate')])

                        if leave:
                            remark = "LEAVE"
                            print 'date', rec.date
                            print 'leave type', leave
                            absence_line = self.env['hr.policy.line.absence'].search(
                                [('holiday_status_id', '=', leave.holiday_status_id.id),
                                 ('policy_id', 'in', p_list)])
                            print 'absence_line', absence_line

                            if absence_line.type == 'paid':
                                paid_pay = daily_rate * (absence_line.rate / 100)
                                paid += paid_pay
                                _create_absence_breakdown(self, attn, rec, leave, absence_line, paid, remark)
                            elif absence_line.type == 'unpaid':
                                unpaid_pay = daily_rate * (absence_line.rate / 100)
                                unpaid += unpaid_pay
                                _create_absence_breakdown(self, attn, rec, leave, absence_line, unpaid_pay, remark)
                            elif absence_line.type == 'dock':
                                dock_pay = daily_rate * (absence_line.rate / 100)
                                dock += dock_pay
                                _create_absence_breakdown(self, attn, rec, leave, absence_line, dock_pay, remark)

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
                                    [('calendar_id', '=', self.working_hours.id)])

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
                                        valid_min = min/100
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
                                    late_pay = (late_min/60) * hourly_rate
                                    print 'late_pay',late_pay
                                    late+=late_pay
                                    daily_rate = _get_rate(self, 'daily')
                                    late_rate = (late_pay / daily_rate) * 100
                                    absence_line = ['unpaid', round(late_rate, 2)]
                                    _create_absence_breakdown(self, attn, rec, leave, absence_line, late_pay, remark)

                            else:
                                ut = ((rec.diff * 60) / 100)
                                if ut > valid_min:
                                    remark = 'UT'
                                    # ut_pay = abs(ut) * hourly_rate
                                    ut_pay = abs(rec.diff) * hourly_rate
                                    undertime += ut_pay

                                    # daily_rate = _get_rate('daily', sal)
                                    daily_rate = _get_rate(self,'daily')
                                    ut_rate= (ut_pay/daily_rate) * 100
                                    absence_line = ['unpaid',round(ut_rate,2)]
                                    _create_absence_breakdown(self, attn, rec, leave, absence_line, ut_pay, remark)



                        else:
                            holiday = self.env['hr.holidays.public.line'].search([('date','=',rec.date)])
                            # holiday_type = self.env['hr.holidays.public.type'].browse(holiday)
                            if holiday:
                                remark = "HOL"
                                absence_line = self.env['hr.policy.line.absence'].search(
                                    [('use_holiday', '=', True),
                                     ('policy_id', 'in', p_list),
                                     ('holiday_id','=',holiday.holiday_type.id)])

                                if absence_line:
                                    holi_pay = rec.duty_hours * hourly_rate
                                    holi += holi_pay
                                    absence_line = ['paid', 100]
                                    _create_absence_breakdown(self, attn, rec, leave, absence_line, holi_pay, remark)

                            else:
                                remark = "ABS"
                                abs_pay = rec.duty_hours * hourly_rate
                                absent += abs_pay
                                absence_line = ['unpaid', 100]
                                _create_absence_breakdown(self, attn, rec, leave, absence_line, abs_pay, remark)

                    absent_pay = absent + unpaid + undertime + late
                else:
                    # if self.working_hours.work_type == 'flexi':
                    #     flexi = self.env['resource.calendar.attendance'].search([('calendar_id','=',self.working_hours.id)])
                    #     flex_hours_week = flexi.flex_week_hours
                    #     valid_abs = 0
                    #     if flex_hours_week == 40:
                    #         valid_abs = 2
                    #     elif flex_hours_week == 48:
                    #         valid_abs = 1
                    #
                    #     timesheet_sum = self.env['hr_timesheet.summary'].search(
                    #         [('employee_id', '=', self.employee_id.id),
                    #          ('duty_hours', '!=', 0.00),
                    #          ('actual_worked_hours', '<', 8.00),
                    #          # ('diff', '<', 0.00),
                    #          ('date', '>=', payslip.date_from),
                    #          ('date', '<=', payslip.date_to)])
                    absent_pay = 0.00
            else:
                if abs_days > 0:
                    absent_pay = abs_days * daily_rate
        return round(absent_pay, 2)

    def _get_overtime(self,payslip):
        work_days = payslip.worked_days_line_ids

        # for rec in work_days:
        #     ot = self.env['hr.payslip.worked_days'].search([('code', '=', 'OT'),
        #                                                     ('contract_id', '=', self.id),
        #                                                     ('payslip_id', '=', payslip.id)])
        #     work100 = self.env['hr.payslip.worked_days'].search([('code', '=', 'WORK100'),
        #                                                     ('contract_id', '=', self.id),
        #                                                     ('payslip_id', '=', payslip.id)])
        #     attn = self.env['hr.payslip.worked_days'].search([('code', '=', 'ATTN'),
        #                                                     ('contract_id', '=', self.id),
        #                                                     ('payslip_id', '=', payslip.id)])

        ot = _get_work_days(self,payslip,work_days,'OT')
        work100 = _get_work_days(self, payslip, work_days, 'WORK100')
        attn = _get_work_days(self,payslip,work_days,'ATTN')

        if ot:
            holiday_ot = 0.00
            daily_ot = 0.00
            restday_ot = 0.00
            restholiday_ot = 0.00
            sal = self.wage
            # hourly_rate = _get_rate('hrs',sal)
            hourly_rate = _get_rate(self,'hrs')

            if self.policy_id.id:
                policy_group_id = self.policy_id.id
                print policy_group_id
                self.env.cr.execute(
                    "SELECT group_id, ot_id from hr_policy_group_ot_rel where group_id = \'%s\'" % policy_group_id)
                res = self.env.cr.fetchall()
                print 'recs>>>', res

                p_list = []
                for r in res:
                    print r[1]
                    overtime_id = r[1]
                    p_list.append(r[1])
                print 'pList', p_list

                timesheet_sum = self.env['hr_timesheet.summary'].search([('employee_id', '=', self.employee_id.id),
                                                                         # ('auth_ot', '!=', 0.00),
                                                                         ('actual_ot', '!=', 0.00),
                                                                         ('date', '>=', payslip.date_from),
                                                                         ('date', '<=', payslip.date_to)])



                for rec in timesheet_sum:
                    print 'date', rec.date

                    if_import = _check_timesheet(self, rec.sheet_id.id)

                    #if HOLIDAY POLICY
                    if self.env['hr.holidays.public.line'].search([('date', '=', rec.date)]):
                        holiday = self.env['hr.holidays.public.line'].search([('date', '=', rec.date)])
                        holiday_type = self.env['hr.holidays.public.type'].search(
                            [('id', '=', holiday.holiday_type.id)])
                        # IF HOLIDAY ONLY
                        if rec.duty_hours:
                            policy_lines = self.env['hr.policy.line.ot'].search([('holiday_id','=',holiday_type.id),
                                                                                 ('type', '=', 'holiday'),
                                                                                ('policy_id','in',p_list)])

                            if not if_import:
                                    holiday = ((hourly_rate * (policy_lines.rate / 100)) * rec.actual_worked_hours)
                                    # holiday = holiday_test/2
                            else:
                                holiday = ((hourly_rate * (policy_lines.rate / 100)) * (rec.actual_ot + rec.actual_worked_hours))
                                # holiday = holiday_test / 2
                            _create_overtime_breakdown(self,ot, rec, policy_lines, holiday)
                            holiday_ot += holiday / 2

                        # IF RESTDAY ON OHOLIDAY
                        else:
                            print 'restday on holiday'
                            policy_lines = self.env['hr.policy.line.ot'].search([('holiday_ids', '=', holiday_type.id),
                                                                             ('type', '=', 'rest_on_holiday'),
                                                                             ('policy_id', 'in', p_list)])
                            if not if_import:
                                restholiday_test= ((hourly_rate * (policy_lines.rate / 100)) * rec.actual_worked_hours)
                                restholiday = ((hourly_rate * ((policy_lines.rate - 100) / 100)) * rec.actual_worked_hours)
                            else:
                                restholiday_test = ((hourly_rate * (policy_lines.rate / 100)) * (rec.actual_worked_hours+ rec.actual_ot))
                                restholiday = (
                                (hourly_rate * ((policy_lines.rate - 100) / 100)) * (rec.actual_worked_hours + rec.actual_ot))

                            _create_overtime_breakdown(self,ot, rec, policy_lines, restholiday_test)

                            restholiday_ot += restholiday

                    #if DAILY POLICY
                    elif rec.duty_hours:
                        policy_lines = self.env['hr.policy.line.ot'].search([('type', '=', 'daily'),
                                                                             ('policy_id', 'in', p_list)])

                        daily = ((hourly_rate * (policy_lines.rate / 100)) * rec.actual_ot)
                        daily_ot += daily

                        _create_overtime_breakdown(self,ot,rec,policy_lines,daily)

                    #if RESTDAY POLICY
                    else:
                        policy_lines = self.env['hr.policy.line.ot'].search([('type', '=', 'restday'),
                                                                             ('policy_id', 'in', p_list)])
                        # restday_ot += ((hourly_rate * (policy_lines.rate / 100)) * rec.actual_ot)
                        restday = ((hourly_rate * (policy_lines.rate / 100)) * rec.actual_ot)
                        restday_ot += restday

                        _create_overtime_breakdown(self,ot, rec, policy_lines, restday)
                ot_pay = holiday_ot + daily_ot + restday_ot + restholiday_ot
            else:
                ot_hrs = ot.number_of_hours
                ot_pay = ot_hrs * hourly_rate
            # ot_pay = holiday_ot + daily_ot + restday_ot + restholiday_ot
            print 'DAILY OT', daily_ot
            print 'RESTDAY OT', restday_ot
            print 'HOLIDAY OT', holiday_ot
            print 'RESTHOLIDAY', restholiday_ot
        else:
            #if daily-weekly
            if self.schedule_pay == 'weekly':
                work100 = work100.number_of_days
                attn = attn.number_of_days
                if attn > work100:
                    ot_pay = (attn - work100) * self.wage
            else:
                ot_pay = 0.00
        return ot_pay

    def _get_13thpay(self,payslip):
        work_days = payslip.worked_days_line_ids

        attn = _get_work_days(self, payslip, work_days, 'ATTN')
        actual_hrs = attn.number_of_hours
        sched_pay = self.schedule_pay
        s_pay_type = self.payroll_type
        sal = self.wage
        if actual_hrs:
            if sched_pay == 'monthly':
                freq = 12
            elif sched_pay == 'semi-monthly':
                freq = 24
            elif sched_pay == 'weekly':
                freq = 52.14
            else:
                sal = self.wage
                freq = 1

            if s_pay_type == 'daily':
                _13th_rate = sal

            elif s_pay_type == 'monthly':
                _13th_rate = sal


            year_start = date(date.today().year, 1, 1)
            year_end = date(date.today().year, 12, 31)
            # prev_13thpay =self.env['hr.payslip.line'].search([('employee_id','=',self.employee_id.id),
            #                                      ('contract_id', '=', self.id),
            #                                      ('code','=','A13MPAY'),
            #                                      ('slip_id.state','=','done'),
            #                                      ('slip_id.date_from','>=',year_start),
            #                                      ('slip_id.date_to','<=',year_end)],order='slip_id desc', limit=1)

            prev_13thpay = self.env['hr.payslip.line'].search([('employee_id', '=', self.employee_id.id),
                                                               ('contract_id', '=', self.id),
                                                               ('code', '=', 'A13MPAY'),
                                                               ('slip_id.state', '=', 'done'),
                                                               ('slip_id.date_from', '>=', year_start),
                                                               ('slip_id.date_to', '<=', year_end)])

            abs = self._get_absent(payslip)
            print 'abs', abs

            sum = 0.00
            # for res in prev_13thpay:
            #     sum += res.total
            # _13thpay = sum + ((_13th_rate / freq) - abs)
            for res in prev_13thpay:
                sum += res.monthly_13th_pay
            _13thpay = sum + ((_13th_rate / freq) - abs)
        else:
            _13thpay = 0

        print _13thpay
        return round(_13thpay,2)

    def _get_gross(self,categ):
        gross = categ.BASIC + categ.ALW + categ.OT + categ.OIT
        return round(gross, 2)

    def _get_net(self,categ):
        net = (categ.GROSS + categ.OINT + (categ.ADJ)) - categ.DED
        return round(net, 2)

    def check_emp_tax_status(self, wtax_contri, emp_id):
        if wtax_contri:
            if not emp_id.tin_type:
                raise ValidationError("Please set your Tax Status in your Personal Info")

    @api.model
    def create(self, vals):
        if vals['employee_id']:
            employee_id = self.env['hr.employee'].browse(vals['employee_id'])
            if vals['wage']:
                employee_id.write({'wage': vals['wage']})
            if vals['schedule_pay']:
                print 'sched_pay', vals['schedule_pay']
                employee_id.write({'schedule_pay': str(vals['schedule_pay'])})
            if vals['payroll_type']:
                employee_id.write({'pay_type': str(vals['payroll_type'])})
            if vals['department_id']:
                employee_id.write({'department_id':vals['department_id']})
            if vals['job_id']:
                employee_id.write({'job_id': vals['job_id']})
            wtax_contri = vals['wtax_contri']
            self.check_emp_tax_status(wtax_contri,employee_id)
        return super(Hr_Contract, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(Hr_Contract, self).write(vals)
        if self.employee_id:
            if self.wage:
                self.employee_id.write({'wage': self.wage})
                if self.schedule_pay:
                    self.employee_id.write({'schedule_pay': str(self.schedule_pay)})
                if self.payroll_type:
                    self.employee_id.write({'pay_type': str(self.payroll_type)})
                if self.department_id:
                    self.employee_id.write({'department_id': self.department_id.id})
                if self.job_id:
                    self.employee_id.write({'job_id': self.job_id.id})
            wtax_contri = self.wtax_contri
            self.check_emp_tax_status(wtax_contri, self.employee_id)
        return res

class Hr_Overtime_Breakdown(models.Model):
    _name ='hr.overtime.breakdown'
    _description = 'HR Overtime Breakdown'

    worked_days_id = fields.Many2one('hr.payslip.worked_days',string="Payslip" ,ondelete='cascade')
    code = fields.Char(string="Code")
    date = fields.Date(string = "Date")
    auth_ot = fields.Float(string="Authorized OT")
    act_ot = fields.Float(string="Actual OT")
    type = fields.Selection([('daily', 'Daily'),
                             ('restday', 'Rest Day'),
                             ('holiday', 'Public Holiday'),
                             ('rest_on_holiday', 'Restday on Holiday')],
                            string="Type", required=True)
    rate = fields.Float(string="Rate(%)")
    amount = fields.Float(string="Amount")

class Hr_Absence_Breakdown(models.Model):
    _name ='hr.absence.breakdown'
    _description = 'HR Absence Breakdown'

    worked_days_id = fields.Many2one('hr.payslip.worked_days',string="Payslip" ,ondelete='cascade')
    code = fields.Char(string="Code")
    date = fields.Date(string = "Date")
    duty_hours = fields.Float(string="Duty Hours")
    auth_abs = fields.Float(string="Authorized Leave Day")
    act_abs = fields.Float(string="Actual Worked")
    leave_id = fields.Many2one('hr.holidays.status', 'Leave')
    type = fields.Selection([('paid', 'Paid'),
                             ('unpaid', 'Unpaid'),
                             ('dock', 'Dock')],
                             string ="Type")
    rate = fields.Float(string="Rate(%)")
    amount = fields.Float(string="Amount")
    remark = fields.Char(string="Remark")

class Hr_Payslip_Worked_Days(models.Model):
    _inherit = 'hr.payslip.worked_days'
    _description = 'Inherit Hr Payslip Worked Days'

    overtime_breakdown_ids = fields.One2many('hr.overtime.breakdown','worked_days_id',string ="Overtime Breakdown" ,ondelete='cascade')
    absence_breakdown_ids = fields.One2many('hr.absence.breakdown','worked_days_id',string ="Absence Breakdown" ,ondelete='cascade')

class Employee(models.Model):
    _inherit ='hr.employee'

    tin_type = fields.Many2one('payroll.tax.status', string="TAX Status")
    contract_ids = fields.One2many('hr.contract','employee_id', string="Contract")

class Hr_Payslip(models.Model):
    _inherit ='hr.payslip'
    _order = 'date_from desc'

    @api.onchange('payslip_run_id')
    def onchange_payslip_run_id(self):
        # super(HrPayslip, self).onchange_payslip_run_id()

        payslip_run = self.payslip_run_id

        print 'HERE'
        if payslip_run:
            period = payslip_run.hr_period_id
            self.hr_period_id = period.id
            if period:
                self.name = self.employee_id.name

    @api.one
    @api.constrains('hr_period_id', 'company_id')
    def _check_period_company(self):
        contract_id = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                      ('id', '=', self.contract_id.id)])
        company_id = self.env['res.partner'].search([('id', '=', contract_id.partner_id.id)])
        if self.hr_period_id:
            if self.hr_period_id.company_id != company_id:
                raise ValidationError(
                    "The company on the selected period must "
                    "be the same as the company on the "
                    "payslip."
                )
        return True

    @api.model
    def get_inputs(self, contract_ids, date_from, date_to):
        res = []

        contracts = self.env['hr.contract'].browse(contract_ids)
        structure_ids = contracts.get_all_structures()
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
        inputs = self.env['hr.salary.rule'].browse(sorted_rule_ids).mapped('input_ids')

        for contract in contracts:
            # if contract.working_hours.work_type == 'daily':
            #     cash_advance = {
            #         'name': 'Cash Advance',
            #         'code': 'CA',
            #         'contract_id': contract.id,
            #     }
            #     res += [cash_advance]
            # else:
            #     for input in inputs:
            #         input_data = {
            #             'name': input.name,
            #             'code': input.code,
            #             'contract_id': contract.id,
            #         }
            #         res += [input_data]

            cash_advance = {
                'name': 'Cash Advance',
                'code': 'CA',
                'contract_id': contract.id,
            }
            # res += [cash_advance]
            allowance = {
                'name': 'Allowance',
                'code': 'ALW',
                'contract_id': contract.id,
            }

            other_income_tax = {
                'name': 'Other Income Taxable',
                'code': 'OIT',
                'contract_id': contract.id,
            }

            other_income_ntax = {
                'name': 'Other Income Non-Taxable',
                'code': 'OINT',
                'contract_id': contract.id,
            }

            adjustment = {
                'name': 'Adjustment',
                'code': 'ADJ',
                'contract_id': contract.id,
            }
            res += [cash_advance,allowance,other_income_tax,other_income_ntax,adjustment]
        return res

class Hr_Payslip_Worked_days(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.onchange('number_of_days')
    def onchange_num_days(self):
        self.number_of_hours = self.number_of_days * 8

class Hr_Payslip_Line(models.Model):
    _inherit ='hr.payslip.line'

    employer_share = fields.Float(string="Employer Share")
    monthly_13th_pay = fields.Float(string="Monthly 13th Pay")

    def _determine_employer_share(self,company,rec_slip_id,contract,model,freq):
        if company.schedule_pay == 'semi-monthly':
            freq = 1
            vale_1 = False
            vale_2 = False

            date_from = datetime.strptime(rec_slip_id.date_from, "%Y-%m-%d").date()

            if date_from.day >= 1 and date_from.day <= 15:
                vale_1 = True
            else:
                vale_2 = True

            if company.value == 'first':
                if vale_1:
                    emplyr_share = _compute_contri(contract, '', freq, model)

                else:
                    emplyr_share = 0.00

            elif company.value == 'second':
                if vale_2:
                    emplyr_share = _compute_contri(contract, '', freq, model)

                else:
                    emplyr_share = 0.00
        else:
            emplyr_share = _compute_contri(contract, '', freq, model)
        return emplyr_share

    def create(self,vals):
        freq = 0
        abs = 0
        if vals['slip_id']:
            slip_id = vals['slip_id']
            rec_slip_id = self.env['hr.payslip'].browse(slip_id)
            sal = rec_slip_id.contract_id.wage
            contract = rec_slip_id.contract_id
            sched_pay = rec_slip_id.contract_id.schedule_pay
            partner_id = rec_slip_id.contract_id.partner_id

            company = self.env['res.partner'].search([('id', '=', partner_id.id)])

            # if company.sss_contri:
            if company.schedule_pay == 'monthly':
                freq = 2
                if sched_pay == 'monthly':
                    freq = 1
            elif company.schedule_pay == 'semi-monthly':
                freq = 1
            elif company.schedule_pay == 'weekly':
                freq = 4

            if vals['code'] == 'SSS':
                model = 'payroll.sss.matrix'
                emplyr_share = self._determine_employer_share(company,rec_slip_id,contract,model,freq)
                vals['employer_share'] = emplyr_share

            elif vals['code'] == 'PHILHEALTH':
                model = 'payroll.philhealth.matrix'
                emplyr_share = self._determine_employer_share(company, rec_slip_id, contract, model, freq)
                vals['employer_share'] = emplyr_share

            elif vals['code'] == 'PAGIBIG':
                model = 'payroll.pagibig.matrix'
                emplyr_share = self._determine_employer_share(company, rec_slip_id, contract, model, freq)
                vals['employer_share'] = emplyr_share
            elif vals['code'] == 'ABS':
                abs = vals['amount']

            elif vals['code'] == 'A13MPAY':
                contract = self.env['hr.contract'].browse(vals['contract_id'])
                sched_pay = contract.schedule_pay
                sal = contract.wage

                if sched_pay == 'monthly':
                    freq = 12
                elif sched_pay == 'semi-monthly':
                    freq = 24
                elif sched_pay == 'weekly':
                    freq = 52.14

                print 'ABS', abs
                print 'SELF', self
                print 'VALS', vals

                _13th_rate = sal
                monthly_13th_pay = ((_13th_rate / freq) - abs)
                vals['monthly_13th_pay'] = round(monthly_13th_pay,2)

        super (Hr_Payslip_Line, self).create(vals)

    def write(self, vals):

        if vals['slip_id']:
            slip_id = vals['slip_id']
            rec_slip_id = self.env['hr.payslip'].browse(slip_id)
            sal = rec_slip_id.contract_id.wage
            contract = rec_slip_id.contract_id
            sched_pay = rec_slip_id.contract_id.schedule_pay
            partner_id = rec_slip_id.contract_id.partner_id

            company = self.env['res.partner'].search([('id', '=', partner_id.id)])

            if company.sss_contri:
                if company.schedule_pay == 'monthly':
                    freq = 2
                    if sched_pay == 'monthly':
                        freq = 1
                elif company.schedule_pay == 'semi-monthly':
                    freq = 1
                elif company.schedule_pay == 'weekly':
                    freq = 4

            if vals['code'] == 'SSS':
                if vals['total'] == 0.00:
                    vals['employer_share'] = 0.00
                else:
                    sss_id = self.env['payroll.sss.matrix'].search(
                        [('sal_range_min', '<=', sal), ('sal_range_max', '>=', sal)])

                    emplyr_share = sss_id.employer_share / freq
                    vals['employer_share'] = emplyr_share

            elif vals['code'] == 'PHILHEALTH':
                if vals['total'] == 0.00:
                    vals['employer_share'] = 0.00
                else:
                    philhealth_id = self.env['payroll.philhealth.matrix'].search(
                        [('sal_range_min', '<=', sal), ('sal_range_max', '>=', sal)])

                    emplyr_share = philhealth_id.employer_share / freq
                    vals['employer_share'] = emplyr_share

            elif vals['code'] == 'PAGIBIG':
                if vals['total'] == 0.00:
                    vals['employer_share'] = 0.00
                else:
                    pagibig_id = self.env['payroll.pagibig.matrix'].search(
                        [('sal_range_min', '<=', sal), ('sal_range_max', '>=', sal)])

                    emplyr_share = pagibig_id.employer_share / freq
                    vals['employer_share'] = emplyr_share

        super(Hr_Payslip_Line, self).create(vals)

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    emp_exclude_count = fields.Integer(string="Payslip Computation Details")
    # Xemployee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees')
    @api.model
    def default_get(self, fields):
        result = super(HrPayslipEmployees, self).default_get(fields)
        context = self.env.context
        if 'company_id' in context:
                company_id = context['company_id']
        else:
            company_id = ''
        if 'schedule_pay' in context:
            schedule_pay = context['schedule_pay']
        else:
            schedule_pay = ''
        if 'date_payment' in context:
            date_payment = context['date_payment']
        else:
            date_payment = ''
        if 'date_start' in context:
            date_start = context['date_start']
        else:
            date_start = ''
        if 'date_end' in context:
            date_end = context['date_end']
        else:
            date_end = ''

        print 'sch', schedule_pay
        print 'company_id', company_id
        contract_ids = self.env['hr.contract'].sudo().search([('schedule_pay', '=', schedule_pay)
                                                       ,('partner_id','=',company_id)
                                                       ,('state','!=','close')])
        print 'contract_ids',contract_ids
        emp_ids=[]
        count = 0
        for id in contract_ids:
            if schedule_pay != 'weekly':
                #check if the employee has a approved timesheet
                timesheet = self.env['hr_timesheet_sheet.sheet'].sudo().search([('employee_id','=',id.employee_id.id),
                                                                         ('state','=','done'),
                                                                         ('date_from','=',date_start),
                                                                         ('date_to','=',date_end)])
                if timesheet:
                    #check if it has still draft payslip
                    payslip = self.env['hr.payslip'].search([('contract_id','=',id.id),
                                                                  ('date_from','=',date_start),
                                                                  ('date_to','=',date_end),
                                                                  ('state','=','draft')])
                    if not payslip:
                        emp_ids.append(id.employee_id.id)
                else:
                    count += 1
            else:
                emp_ids.append(id.employee_id.id)
        result['emp_exclude_count'] = count
        result['employee_ids'] = emp_ids
        return result

class Excluded_Employee(models.Model):
    _name = 'excluded.employee'

    name = fields.Char(string="Name")
    payslip_run_id = fields.Many2one('hr.payslip.run',string="payslip Run ID", ondelete="cascade")

class Hr_Payslip_Run(models.Model):
    _inherit = 'hr.payslip.run'

    ex_emp_count = fields.Integer(compute ='_compute_emp_count', string="Payslip not generated")
    payslip_count = fields.Integer(compute='_compute_payslip_count', string="Payslip generated")
    exclude_emp_ids = fields.One2many('excluded.employee','payslip_run_id',string="Exempted Employee")

    @api.multi
    def _compute_payslip_count(self):
        for payslip in self:
            payslip.payslip_count = len(payslip.slip_ids)

    @api.multi
    def _compute_emp_count(self):
        contract_ids = self.env['hr.contract'].sudo().search([('schedule_pay', '=', self.schedule_pay)
                                                                 , ('partner_id', '=', self.company_id.id)
                                                                 , ('state', '!=', 'close')])
        count = 0
        for id in contract_ids:
            # check if the employee has a approved timesheet
            timesheet = self.env['hr_timesheet_sheet.sheet'].sudo().search([('employee_id', '=', id.employee_id.id),
                                                                            ('state', '=', 'done'),
                                                                            ('date_from', '=', self.date_start),
                                                                            ('date_to', '=', self.date_end)])
            if not timesheet:
                count += 1
                if self.payslip_count:
                    check_emp = self.env['excluded.employee'].search([('payslip_run_id','=',self.id),
                                                          ('name','=',id.employee_id.name_related)])
                    if not check_emp:
                        self.exclude_emp_ids.create({
                            'name': id.employee_id.name_related,
                            'payslip_run_id': self.id})
        self.ex_emp_count = count

    def act_employee(self):
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'excluded.employee',
            'domain': [
                ('payslip_run_id', '=', self.id),
            ],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            'name':'Excluded Employee'}


    def act_payslips(self):
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.payslip',
            'domain': [
                ('payslip_run_id', '=', self.id),
            ],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            'name':'Included Employee'}
