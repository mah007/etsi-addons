from odoo import fields, api, models

class LeavesReport(models.TransientModel):
    _name = 'summary_leave_report.wizard'

    employee = fields.Many2one('hr.employee', string="Employee name")
    from_date = fields.Date(string="Starting Date")
    to_date = fields.Date(string="Ending Date")

    def print_leaves(self, data):
        data = {}

        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['employee', 'from_date', 'to_date'])[0]
        return self.env['report'].sudo().get_action(self, 'etsi_hrms.report_leaves_summary', data=data)
