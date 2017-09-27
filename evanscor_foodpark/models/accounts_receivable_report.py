from odoo import fields,api,models

class AccountsReceivableReport(models.Model):
    _name = 'accounts.receivable.report'

    customer_name = fields.Many2one('res.partner', string='Customer Name')
    invoice_number = fields.Many2many('account.invoice', string='Invoice Number')

    @api.onchange('customer_name')
    def onchange_cust_id(self):

        res_invoice_number = self.env['account.invoice'].search([('partner_id', '=', self.customer_name.id)])
        self.invoice_number = res_invoice_number

    def print_accounts_receivable_report(self, data):
        data = {}

        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['customer_name'])[0]
        return self.env['report'].sudo().get_action(self, 'evanscor_foodpark.report_accounts_receivable_template', data=data)

