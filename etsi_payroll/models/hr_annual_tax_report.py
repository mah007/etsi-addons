from odoo import fields,api,models
from datetime import datetime

class AnnualTaxReport(models.Model):
    _name = 'hr.payroll.annual.tax.report'


    this_year = datetime.today().year
    range_of_years = range(this_year - 40, this_year + 1)
    descending_range = sorted(range_of_years, reverse=True)
    _get_years = [(str(x), str(x)) for x in descending_range]
    current_year = str(this_year)
    year_selection = fields.Selection(_get_years, string="Select Year", default=current_year)

    annual_company_id = fields.Many2one('res.partner', string='Company',required=True, domain=[('is_company','=', True)])

    def print_annual_tax_report(self, data):
        data = {}

        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['annual_company_id', 'year_selection'])[0]
        return self.env['report'].sudo().get_action(self, 'etsi_payroll.report_annual_tax_template', data=data)

