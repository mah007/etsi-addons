from odoo import models, fields


class EmployeeTimesheet(models.TransientModel):
    _name = 'hr.payroll.register'

    company = fields.Many2one('res.partner', string="Company", domain=[('is_company', '=', True)])
    from_date = fields.Date(string="Starting Date")
    to_date = fields.Date(string="Ending Date")


    def print_payroll_register(self, data):
        """Redirects to the report with the values obtained from the wizard
        'data['form']': name of employee and the date duration"""
        data = {}
        data['form'] = self.read(['company', 'from_date', 'to_date'])[0]
        return self.env['report'].get_action(self, 'etsi_payroll.report_payroll_register', data=data)