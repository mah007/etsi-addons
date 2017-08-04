from odoo import models, fields, api

class CompanyInfo(models.AbstractModel):
    _name = 'report.etsi_payroll.report_annual_tax_template'

    @api.multi
    def render_html(self, docids, data={}):
        context = dict(self.env.context or {})
        data = data if data is not None else {}
        model = context.get('active_model') or context.get('model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        if 'annual_company_id' in data['form']:
            if data['form']['annual_company_id']:
                annual_company_id = data['form']['annual_company_id']
                # comp_name = data['form']['comp_id'][1] OTHER WAYS
            else:
                annual_company_id = False

        else:
            annual_company_id = False

        res_comp = self.env['hr.employee'].search([('company_id', '=', annual_company_id[0])])

        for e in res_comp:
            res_payroll = self.env['hr.payslip.line'].search([('employee_id', '=', e.id), ('code', '=', 'TAX')])
            tax_sum = 0

            annual_tax = []
            for res_tax in res_payroll:
                tax_sum += res_tax.amount

            annual_tax.append((res_tax.employee_id, res_payroll[0].code, tax_sum))

            return annual_tax



        data.update({'company_employee': res_comp})


        docargs = {
            'doc_ids':context['active_ids'],
            'doc_model': model,
            'data': data,
            'docs': docs,
            # 'comp_name': comp_id[1], #other ways
        }
        return self.env['report'].render('etsi_payroll.report_annual_tax_template', docargs)