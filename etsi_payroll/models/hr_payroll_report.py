from odoo import models, fields, api, time


def get_years():
    year_list = []
    for i in range(2016, 2036):
        year_list.append((i, str(i)))
    return year_list

class EmployeePayrollReport(models.Model):
    _name = 'hr.payroll.report'

    com_id= fields.Many2one('res.partner', string="Company", domain=[('is_company','=', True)])
    year_date = fields.Selection(get_years(), string='Year',)
    # year_date = fields.Selection([(num, str(num)) for num in range(2000, (fields.datetime.now().year) + 1)], 'Year')

    @api.multi
    def print_company_annual_tax(self, data):
        data = {}

        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['com_id', ])[0]
        print 'data', data

        return self.env['report'].sudo().get_action(self, 'etsi_payroll.report_annual_tax_report', data=data)

        # data = {}
        # data['form'] = self.read(['com_id',])[0]
        # return self.env['report'].get_action(self, 'etsi_payroll.report_annual_tax_report', data=data)