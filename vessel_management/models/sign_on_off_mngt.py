
from odoo import fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from dateutil import relativedelta

class SignOnManagement(models.Model):
    _name = "sign_on.management"

    employee_id = fields.Many2one('hr.employee', string="Seaman")
    sign_on_date = fields.Date(string="Sign On Date", default=lambda *a:datetime.today())
    country_id = fields.Many2one('res.country', string="Country")
    port_embark_id = fields.Many2one('port.embarkation', string="Port")
    contract = fields.Text(type="text",
                           string="Contract", readonly=True)
    state = fields.Selection([('draft', 'Draft'),('confirmed','Confirm')], string="Status", default='draft')

    @api.model
    def default_get(self, fields):

        result = super(SignOnManagement, self).default_get(fields)
        context = self.env.context
        if context:
            if 'emp_id' in context:
                if context['emp_id']:
                    result['employee_id'] = context['emp_id']
        return result

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.contract = _get_contract_display(self)

    @api.onchange('country_id')
    def onchange_port_embark_id(self):
        self.port_embark_id = False
        return {'domain': {'port_embark_id': [('country_id', '=', self.country_id.id)]},}


    @api.multi
    def sign_on_confirm(self):
        self.employee_id.write({'status':'onboard'})
        self.state = 'confirmed'
        res_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id), ('state', '!=', 'close')])
        if res_contract:
            vessel_id = ''
            for cntrct in res_contract:
                vessel_id = cntrct.vessel_id.id
            if vessel_id:
                self.env['crew.onboard'].create({'vessel_id':vessel_id,'employee_name':self.employee_id.name,'first_name':self.employee_id.first_name,
                                                 'middle_name':self.employee_id.middle_name,'last_name':self.employee_id.last_name,
                                                'contract_name':cntrct.name,'sign_on':self.sign_on_date,'contract':_get_contract_display(self),
                                                 'port_embark':self.port_embark_id.name})
        else:
            raise ValidationError('Unable to Sign On. Seaman has no Contract.')

class SignOffManagement(models.Model):
    _name = "sign_off.management"

    employee_id = fields.Many2one('hr.employee', string="Seaman")
    sign_off_date = fields.Date(string="Sign Off Date", default=lambda *a:datetime.today())
    country_id = fields.Many2one('res.country', string="Country")
    port_embark_id = fields.Many2one('port.embarkation', string="Port")
    contract = fields.Text(type="text",
                           string="Contract", readonly=True)
    state = fields.Selection([('draft', 'Draft'),('confirmed','Confirm')], string="Status", default='draft')
    reason = fields.Text(string="Reason")

    @api.model
    def default_get(self, fields):

        result = super(SignOffManagement, self).default_get(fields)
        context = self.env.context
        if context:
            if 'emp_id' in context:
                if context['emp_id']:
                    print 'yes', context['emp_id']
                    result['employee_id'] = context['emp_id']
        return result

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.contract = _get_contract_display(self)

    @api.onchange('country_id')
    def onchange_port_embark_id(self):
        self.port_embark_id = False
        return {'domain': {'port_embark_id': [('country_id', '=', self.country_id.id)]}, }

    @api.multi
    def sign_off_confirm(self):
        context = self.env.context
        sign_on_date = context['sign_on']
        res_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id), ('state', '!=', 'close')])[0]
        res_contract.employee_id.write({'status':'offboard'})
        date1 = datetime.strptime(self.sign_off_date, '%Y-%m-%d')
        date2 = datetime.strptime(sign_on_date, '%Y-%m-%d')
        get_date = relativedelta.relativedelta(date2, date1)
        duration = str(abs(get_date.years)) + ' year, ' + str(abs(get_date.months)) + ' month, ' + str(abs(get_date.days)) + ' day'

        self.env['sea.services'].create({'emp_id':res_contract.employee_id.id,'vessel_id':res_contract.vessel_id.id,'sign_on':sign_on_date,'sign_off':self.sign_off_date,
                                         'duration':duration})
        crew_onboard_id = context['crew_onboard_id']
        if crew_onboard_id:
            rec_crew_onboard = self.env['crew.onboard'].browse(crew_onboard_id)
            rec_crew_onboard.unlink()



def _get_contract_display(self):
    for rec in self:
        res_contract = self.env['hr.contract'].search([('employee_id','=',rec.employee_id.id),('state','!=','close')])
        job_name = ''
        dept_name = ''
        vessel = ''
        sign_on_date = ''
        wage = ''
        currency = ''
        date_start = ''
        date_end = ''
        duration = ''
        get_month = ''
        for rec in res_contract:
            if rec.job_id:
                job_name = rec.job_id.name
            if rec.department_id:
                dept_name = rec.department_id.name
            if rec.vessel_id:
                vessel = rec.vessel_id.name
            if rec.sign_on:
                sign_on_date = rec.sign_on
            if rec.wage:
                wage = ("{0:,g}".format(rec.wage))
            if rec.currency_id:
                currency = rec.currency_id.name
            if rec.date_start:
                date_start = str(rec.date_start)
            if rec.date_end:
                date_end = str(rec.date_end)
            duration = date_start + ' - ' + date_end
            if rec.months:
                get_month = rec.months
            # if rec.date_start and rec.date_end:
            #     month = datetime.strptime(rec.date_end,'%Y-%m-%d').month  - datetime.strptime(rec.date_start,'%Y-%m-%d').month
            #     days =  datetime.strptime(rec.date_end,'%Y-%m-%d').day  - datetime.strptime(rec.date_start,'%Y-%m-%d').day
            #     get_month = str(abs(month)) + ' months, ' + str(abs(days)) + ' days'



        output = [
            '<style>.attendanceTable td,.attendanceTable th {padding: 10px; border: 1px solid #C0C0C0;} </style><table class="attendanceTable" width="80%">']
        output.append('<tr>')
        output.append('<th style="text-align:center">' + 'RANK' + '</th>')
        output.append('<th style="text-align:center">' + 'DEPARTMENT' + '</th>')
        output.append('<th style="text-align:center">' + 'VESSEL' + '</th>')
        # output.append('<th style="text-align:center">' + 'SIGN ON DATE' + '</th>')
        output.append('<th style="text-align:center">' + 'WAGE' + '</th>')
        output.append('<th style="text-align:center">' + 'CURRENCY' + '</th>')
        # output.append('<th style="text-align:center">' + 'DURATION' + '</th>')
        output.append('<th style="text-align:center">' + 'SIGN ON DATE' + '</th>')
        output.append('<th style="text-align:center">' + 'SIGN OFF DATE' + '</th>')
        output.append('<th style="text-align:center">' + 'MONTHS' + '</th>')
        output.append('</tr>')

        output.append('<tr>')
        output.append('<td style="text-align:center">' + job_name + '</th>')
        output.append('<td style="text-align:center">' + dept_name + '</th>')
        output.append('<td style="text-align:center">' + vessel + '</th>')
        # output.append('<td style="text-align:center">' + sign_on_date + '</th>')
        output.append('<td style="text-align:center" >' + str(wage)+ '</th>')
        output.append('<td style="text-align:center">' + currency + '</th>')
        # output.append('<td style="text-align:center">' + duration + '</th>')
        output.append('<td style="text-align:center">' + date_start + '</th>')
        output.append('<td style="text-align:center">' + date_end + '</th>')
        output.append('<td style="text-align:center">' + get_month + '</th>')
        output.append('</tr>')

        output.append('</table>')
        print 'output', output
        res = '\n'.join(output)
        return res