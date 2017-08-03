from odoo import fields,api,models

class AnnualTaxReport(models.Model):
    _name = 'hr.payroll.annual.tax.report'

    empl_id = fields.Many2one('res.partner', string='Employee')
    year = fields.Selection([(num, str(num)) for num in range(2000, (fields.datetime.now().year) + 1)], 'Year')

