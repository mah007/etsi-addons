from odoo import models, fields, api, time


def get_years():
    year_list = []
    for i in range(2016, 2036):
        year_list.append((i, str(i)))
    return year_list

class EmployeePayrollReport(models.Model):
    _name = 'hr.payroll.report'

    company = fields.Many2one('res.partner', string="Company", domain=[('is_company','=', True)])
    # year_date = fields.Datetime(string="Year")
    # year_date = fields.Date(default=lambda *a: time.strftime('%Y-12-31'))

    year_date = fields.Selection(get_years(), string='Year',)