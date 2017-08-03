from odoo import fields,api,models

class AnnualTaxReport(models.Model):
    _name = 'hr.payroll.annual.tax.report'

    annual_company_id = fields.Many2one('res.partner', string='Company')
    year_selection = fields.Selection([(num, str(num)) for num in range(2000, (fields.datetime.now().year) + 1)], 'Year')

    # def print_payroll_register(self,data):

