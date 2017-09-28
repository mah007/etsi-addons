from odoo import models, fields, api, exceptions

class CompanyInfo(models.AbstractModel):
    _name = 'report.flexerp_pos.report_accounts_receivable_template'

    @api.multi
    def render_html(self, docids, data={}):
        context = dict(self.env.context or {})
        data = data if data is not None else {}
        model = context.get('active_model') or context.get('model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        if 'customer_name' in data['form']:
            if data['form']['customer_name']:
                customer_name = data['form']['customer_name']
            else:
                raise exceptions.ValidationError("Invalid Customer")
        else:
            raise exceptions.ValidationError("Invalid Customer")

        res_cus = self.env['account.invoice'].search([('partner_id', '=', customer_name[0]),('state', '=', 'open')])

        total_paid = 0.00
        cus_invoice = []
        remarks = 'On Process'
        for e in res_cus:
            total_paid = e.amount_total_signed - e.residual_signed
            if e.date_invoice >= e.date_due and e.residual_signed != 0:
                remarks = 'Late Payment'

            if res_cus:
                cus_invoice.append((e.number, e.date_invoice, e.date_due, e.amount_total_signed, e.residual_signed, total_paid, remarks))


        docargs = {
            'doc_ids':context['active_ids'],
            'doc_model': model,
            'data': data,
            'docs': docs,
            'cust_name': e.partner_id.name,
            'cus_invoice': cus_invoice,
        }

        return self.env['report'].render('flexerp_pos.report_accounts_receivable_template', docargs)