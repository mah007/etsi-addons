from odoo import fields,api,models

class AnnualTaxReport(models.Model):
    _name = 'hr.payroll.annual.tax.report'

    annual_company_id = fields.Many2one('res.partner', string='Company')
    year_selection = fields.Selection([(num, str(num)) for num in range(2000, (fields.datetime.now().year) + 1)], 'Year')

    def print_annual_tax_report(self,data):
        data = {}

        data['ids'] = self.env.context.get('active_ids',[])
        data['model'] = self.env.context.get('active_model','ir.ui.menu')
        data['form'] = self.read(['annual_company_id'])[0]
        return self.env['report'].sudo().get_action(self, 'etsi_payroll.report_annual_tax_template', data=data)

