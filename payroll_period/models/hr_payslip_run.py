# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .hr_fiscal_year import get_schedules


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    hr_period_id = fields.Many2one(
        'hr.period',
        string='Period',
        states={'close': [('readonly', True)]}
    )
    schedule_pay = fields.Selection(
        lambda self: self.get_schedule_selection(),
        'Scheduled Pay',
        states={'close': [('readonly', True)]}
    )

    company_id = fields.Many2one(
        'res.partner',
        'Company',
        states={'close': [('readonly', True)]},
        default=lambda self: self.env.user.company_id
    )

    date_payment = fields.Date(
        'Date of Payment',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        # default=lambda self: datetime.now() +
        #                      relativedelta(months=+1, days=-1),
    )

    date_start = fields.Date(string='Date From', required=True, readonly=True,
                             states={'draft': [('readonly', False)]},
                             default='')

    date_end = fields.Date(string='Date To', required=True, readonly=True,
                           states={'draft': [('readonly', False)]},
                           default = '')

    @api.onchange('company_id','hr_period_id')
    def _onchange_company(self):
        if self.company_id:
            company = self.company_id.short_name
        else:
            company = ''

        if self.hr_period_id:
            sched = self.hr_period_id.schedule_pay
        else:
            sched = ''

        if self.hr_period_id:
            pay = self.hr_period_id.date_payment
        else:
            pay = ''

        self.name = "%s - %s(%s)" % (company,sched,pay)



    @api.model
    def get_schedule_selection(self):
        return [
            ('monthly', _('Monthly')),
            ('quarterly', _('Quarterly')),
            ('semi-annually', _('Semi-annually')),
            ('annually', _('Annually')),
            ('weekly', _('Weekly')),
            ('bi-weekly', _('Bi-weekly')),
            ('bi-monthly', _('Bi-monthly')),
            ('semi-monthly', _('Semi-monthly')),
        ]


    @api.multi
    @api.constrains('hr_period_id', 'company_id')
    def _check_period_company(self):
        for run in self:
            if run.hr_period_id:
                if run.hr_period_id.company_id != run.company_id:
                    raise UserError("The company on the selected period must "
                                    "be the same as the company on the  "
                                    "payslip batch.")
        return True

    @api.multi
    @api.constrains('hr_period_id', 'schedule_pay')
    def _check_period_schedule(self):
        for run in self:
            if run.hr_period_id:
                if run.hr_period_id.schedule_pay != run.schedule_pay:
                    raise UserError("The schedule on the selected period must "
                                    "be the same as the schedule on the "
                                    "payslip batch.")
        return True

    @api.model
    def get_default_schedule(self, company_id):
        company = self.env['res.company'].browse(company_id)

        fy_obj = self.env['hr.fiscalyear']

        fys = fy_obj.search([
            ('state', '=', 'open'),
            ('company_id', '=', company.id),
        ])

        return (
            fys[0].schedule_pay
            if len(fys) else 'monthly'
        )

    @api.onchange('company_id', 'schedule_pay')
    # @api.one
    def onchange_company_id(self):
        # super(HrPayslipRun, self).onchange_company_id()

        schedule_pay = (
            self.schedule_pay or
            self.get_default_schedule(self.company_id.id)
        )

        if len(self.company_id) and schedule_pay:
            period = self.env['hr.period'].get_next_period(self.company_id.id,
                                                           schedule_pay,)
            #self.hr_period_id = period.id if period else False,

    @api.onchange('hr_period_id')
    def onchange_period_id(self):
        print len(self.hr_period_id)
        if len(self.hr_period_id) == 0:
                self.date_start = ''
                self.date_end = ''
                self.date_payment = ''
                self.schedule_pay = ''
        else:
                self.date_start = self.hr_period_id.date_start
                self.date_end = self.hr_period_id.date_stop
                self.date_payment = self.hr_period_id.date_payment
                self.schedule_pay = self.hr_period_id.schedule_pay

    @api.multi
    @api.returns('hr.employee')
    def get_employees(self):
        res = super(HrPayslipRun, self).get_employees()
        return res.filtered(
            lambda e: e.contract_id.schedule_pay == self.schedule_pay)

    @api.multi
    def get_payslip_employees_wizard(self):
        res = super(HrPayslipRun, self).get_payslip_employees_wizard()
        res['context']['default_schedule_pay'] = self.schedule_pay
        return res

    @api.multi
    def close_payslip_run(self):
        for run in self:
            if next((p for p in run.slip_ids if p.state == 'draft'), False):
                raise UserError("The payslip batch %s still has unconfirmed "
                                "pay slips." % (run.name))

        self.update_periods()
        return super(HrPayslipRun, self).close_payslip_run()

    @api.multi
    def draft_payslip_run(self):
        for run in self:
            run.hr_period_id.button_re_open()
        return super(HrPayslipRun, self).draft_payslip_run()

    @api.multi
    def update_periods(self):
        for run in self:
            period = run.hr_period_id
            if len(period):
                # Close the current period
                period.button_close()

                # Open the next period of the fiscal year
                fiscal_year = period.fiscalyear_id
                next_period = fiscal_year.search_period(
                    number=period.number + 1)

                if next_period:
                    next_period.button_open()

    @api.model
    def create(self, vals):
        period_id = vals['hr_period_id']
        period_ids = self.env['hr.period'].browse(period_id)
        vals['date_start'] = period_ids.date_start
        vals['date_end'] = period_ids.date_stop
        vals['date_payment'] = period_ids.date_payment
        vals['schedule_pay'] = period_ids.schedule_pay

        return super(HrPayslipRun, self).create(vals)

    @api.multi
    def write(self, vals):
        period_id = vals['hr_period_id']
        period_ids = self.env['hr.period'].browse(period_id)
        vals['date_start'] = period_ids.date_start
        vals['date_end'] = period_ids.date_stop
        vals['date_payment'] = period_ids.date_payment
        vals['schedule_pay'] = period_ids.schedule_pay

        return super(HrPayslipRun, self).write(vals)