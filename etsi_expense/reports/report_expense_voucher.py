from odoo import models, fields, api

class expense_voucher_report(models.Model):
    _inherit = 'hr.expense.sheet'

    def print_voucher(self, data):
        data = {}

        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.env.context.get(['name', 'doc_num', 'employee_id', 'accounting_date', 'expense_line_ids'])[0]
        return self.env['report'].sudo().get_action(self, 'etsi_expense.report_expense_voucher', data=data)
