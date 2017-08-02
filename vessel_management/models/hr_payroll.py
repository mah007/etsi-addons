from odoo import models,fields,api,  _
from dateutil.relativedelta import relativedelta
from datetime import datetime, date

class Hr_Payslip(models.Model):
    _inherit = 'hr.payslip'
    seaman = fields.Boolean(string="Seaman")
    in_house = fields.Boolean(string="Inhouse")
    seaman_id = fields.Many2one('hr.employee',string="Seaman", domain=[('seaman', '=', True)])
    vessel_id = fields.Many2one('vessel.management',string="Vessel")
    allottee_ids = fields.One2many('employee.allottee','payslip_id',string="Allottee")

    @api.onchange('employee_id')
    def _onchange_seaman(self):
        emp = self.employee_id

        if emp.seaman == True:
            allot_ids = self.env['employee.allottee'].search([('emp_ids','=',emp.id)])
            self.allottee_ids = allot_ids

    @api.model
    def default_get(self, fields):
        result = super(Hr_Payslip, self).default_get(fields)
        context = self.env.context

        if context:
            if context:
                if 'emp_type' in context:
                    if context['emp_type'] == 'seaman':
                        result['seaman'] = True
                        result['in_house'] = False
                    elif context['emp_type'] == 'in_house':
                        result['seaman'] = False
                        result['in_house'] = True
        return result

    @api.model
    def create(self, vals):
        emp_id = vals['employee_id']

        emp = self.env['hr.employee'].browse(emp_id)
        print 'emp', emp

        if emp.seaman == True:
            # self.env['employee.allottee'].create({
            #     'payslip_id': vals['date_invoice'],
            #     'delivery_date': values['delivery_date'],
            # })
            allot_ids = self.env['employee.allottee'].search([('emp_ids', '=', emp.id)])
            vals['allottee_ids'] = allot_ids

        # print '...>',vals['allottee_ids']

        # period_ids = self.env['hr.period'].browse(period_id)
        # vals['date_start'] = period_ids.date_start
        # vals['date_end'] = period_ids.date_stop
        # vals['date_payment'] = period_ids.date_payment
        # vals['schedule_pay'] = period_ids.schedule_pay

        return super(Hr_Payslip, self).create(vals)


class HR_PayAllot_Run(models.Model):
    _inherit = 'hr.payslip.run'

    vessel_id = fields.Many2one('vessel.management',string="Vessel")
    remittance_id = fields.Many2one('remittance.advice', string="Remittance No.")
    seaman = fields.Boolean(string="Seaman")
    in_house = fields.Boolean(string="InHouse")


    @api.model
    def default_get(self, fields):
        result = super(HR_PayAllot_Run, self).default_get(fields)
        context = self.env.context

        if context:
            if context:
                if 'emp_type' in context:
                    if context['emp_type'] == 'seaman':
                        result['seaman'] = True
                        result['in_house'] = False
                        result['company_id'] = ""
                        result['hr_period_id'] = ""
                    elif context['emp_type'] == 'in_house':
                        result['seaman'] = False
                        result['in_house'] = True
        return result

    @api.onchange('company_id', 'hr_period_id', 'vessel_id', 'schedule_pay', 'date_payment')
    def _onchange_company(self):
        context = self.env.context

        if self.company_id:
            company = self.company_id.name
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

        if self.vessel_id:
            vessel = self.vessel_id.name
        else:
            vessel = ''

        if self.schedule_pay:
            pay1 = self.schedule_pay
        else:
            pay1 = ''

        if self.date_payment:
            sched1 = self.date_payment
        else:
            sched1 = ''


        if self.vessel_id:

            self.name = "%s - %s(%s)" % (vessel, sched1, pay1)
        else:

            self.name = "%s - %s(%s)" % (company, sched, pay)

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    vessel_id = fields.Many2one(
        'vessel.management',
        'Vessel',
        readonly=True
    )

    @api.model
    def default_get(self, fields):
        result = super(HrPayslipEmployees, self).default_get(fields)
        context = self.env.context
        print 'context', context
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
            date_end = context['date_start']
        else:
            date_end = ''

        if 'vessel_id' in context:
            vessel_id = context['vessel_id']
        else:
            vessel_id = ''

        print 'schedule_pay', schedule_pay
        print 'company_id', company_id
        print 'vessel_id', vessel_id
        if company_id:
            print 'for company'
            contract_ids = self.env['hr.contract'].search([('schedule_pay', '=', schedule_pay)
                                                       ,('partner_id','=',company_id)])

            # emp_ids = []
            # for id in contract_ids:
            #     emp_ids.append(id.employee_id.id)
            #
            # result['employee_ids'] = emp_ids

        if vessel_id:
            print 'for vessel'
            contract_ids = self.env['hr.contract'].search([('schedule_pay', '=', schedule_pay)
                                                              , ('vessel_id', '=', vessel_id)])

            print 'contract_ids', contract_ids
            seaman_list =[]
            for rec in contract_ids:
                seaman_list.append(rec.employee_id)

            print 'seaman_list', seaman_list
            allotte_list=[]
            for res in seaman_list:
                print 'res.id', res.id
                allot_ids = self.env['employee.allottee'].search([('emp_ids', '=', res.id)])
                print 'allot_ids', allot_ids
                for id in allot_ids:
                    allotte_list.append(id.partner_id)

            print 'allotte_list', allotte_list

            # emp_ids = []
            # for id in allotte_list:
            #     emp_ids.append(id.id)
            #
            # result['employee_ids'] = emp_ids


        emp_ids=[]
        for id in contract_ids:
            emp_ids.append(id.employee_id.id)

        result['employee_ids'] = emp_ids
        return result