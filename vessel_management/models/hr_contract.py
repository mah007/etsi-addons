
from odoo import fields, models, api
from datetime import datetime, timedelta
from dateutil import relativedelta

class Contract(models.Model):
    _inherit = "hr.contract"

    employee_id = fields.Many2one('hr.employee', string='Employee', required=False)
    vessel_id = fields.Many2one('vessel.management', string="Vessel")
    sign_on = fields.Date(string="Expected Sign On Date", default= lambda *a: datetime.today())
    in_house = fields.Boolean(string="Employee")
    seaman = fields.Boolean(string="Seaman")
    currency_id = fields.Many2one('res.currency', string="Currency")
    contract_date = fields.Date(string="Date", default= lambda *a: datetime.today())
    months = fields.Char(compute='_get_months',string="Months")

    @api.model
    def default_get(self, fields):
        context = self.env.context
        result = super(Contract, self).default_get(fields)
        if context:
            if 'emp_type' in context:
                if context['emp_type'] == 'seaman':
                    result['seaman'] = True
                    result['in_house'] = False
                elif context['emp_type'] == 'in_house':
                    result['seaman'] = False
                    result['in_house'] = True
        return result

    @api.depends('date_start','date_end')
    def _get_months(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                date1 = datetime.strptime(rec.date_start, '%Y-%m-%d')
                date2 = datetime.strptime(rec.date_end, '%Y-%m-%d')
                get_date = relativedelta.relativedelta(date2, date1)
                get_month = str(abs(get_date.years)) + ' year, ' + str(abs(get_date.months)) + ' month, ' + str(abs(get_date.days)) + ' day'
                rec.months = get_month