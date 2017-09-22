# -*- coding: utf-8 -*-

from odoo import models, fields, api

class expense_sheet(models.Model):
    _inherit = 'hr.expense.sheet'

    doc_num = fields.Char()

    @api.multi
    def approve_expense_sheets(self):
        res_seq = self.env['ir.sequence'].search([('code', '=', 'exp.seq')])
        if res_seq:
            code = res_seq.code
            sequence = self.env['ir.sequence'].next_by_code(code)

        self.write({'state': 'approve', 'responsible_id': self.env.user.id, 'doc_num':sequence})
