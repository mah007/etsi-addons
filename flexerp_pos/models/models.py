# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountsRecievable(models.Model):
    _name = 'accounts_recievable.wizard'

    customer_name1 = fields.Many2one('res.partner', string='Customer Name')
    invoice_number1 = fields.One2many('account.invoice', 'partner_id', string='Invoice Number', domain = [('partner_id', '=', 'partner_id')])
    # acc_invoice_date = fields.Date(string='Invoice Date')
    # acc_end_date = fields.Date(string='Due Date')

    # , domain = [('partner_id', '=', customer_name1)]


    def print_accounts(self, data):
        data = {}

        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['acc_customer_name1', 'acc_invoice_number1'])[0]
        return self.env['report'].sudo().get_action(self, 'flexerp_pos.accounts_receivable_info_temp', data=data)