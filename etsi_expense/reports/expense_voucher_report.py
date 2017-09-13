from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ReportVoucher(models.AbstractModel):
    _name = 'report.etsi_expense.expense_voucher_report'

    @api.model
    def render_html(self, docids, data={}):
        context = dict(self.env.context or {})
        data = data if data is not None else {}
        model = context.get('active_model') or context.get('model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        docargs = {
            'doc_ids': docids,
            'doc_model': 'hr.expense.sheet',
            'docs': docs,
            'data': data,
        }
        return self.env['report'].render('etsi_expense.expense_voucher_report', docargs)