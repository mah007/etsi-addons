from odoo import fields,api,models
from datetime import datetime, timedelta

class AnnualTaxReport(models.Model):
    _name = 'hr.payroll.annual.tax.report'

    def _get_years(self):
        this_year = datetime.today().year

        results = [(str(x), str(x)) for x in range(this_year - 40, this_year + 1)]
        return results

    tday = datetime.now().year
    str_date = str(tday)
    annual_company_id = fields.Many2one('res.partner', string='Company',required=True, domain=[('is_company','=', True)], )
    year_selection = fields.Selection(_get_years, string="Select Year", default=str_date)



    def print_annual_tax_report(self, data):
        data = {}

        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['annual_company_id', 'year_selection'])[0]
        return self.env['report'].sudo().get_action(self, 'etsi_payroll.report_annual_tax_template', data=data)

