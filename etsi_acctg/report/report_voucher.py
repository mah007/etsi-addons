from odoo import fields, models, api
from datetime import datetime
from odoo . exceptions import ValidationError


class AccountPayment(models.AbstractModel):
    _name = 'report.etsi_acctg.report_voucher_template'

    @api.multi
    def render_html(self, docids, data={}):
        context = dict(self.env.context or {})
        data = data if data is not None else {}
        model = context.get('active_model') or context.get('model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        today_date_only = str(datetime.today().date())
        today_date = datetime.strptime(today_date_only, "%Y-%m-%d").date()
        cur_date = today_date.strftime("%m-%d-%Y")

        company_id = docs.company_id.id

        sequence = self.env['account.payment'].get_check_voucher_sequence(company_id)


        docargs = {
            'doc_ids': context['active_ids'],
            'doc_models': model,
            'data': data,
            'docs': docs,
            'cur_date': cur_date,
            'sequence': sequence,


        }

        return self.env['report'].render('etsi_acctg.report_voucher_template', docargs)




