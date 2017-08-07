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

        annual_tax = []
        for e in res_comp:
            res_payroll = self.env['hr.payslip.line'].search([('employee_id', '=', e.id), ('code', '=', 'TAX')])
            print res_payroll
            tax_sum = 0
            tax_name = ''

            for res_tax in res_payroll:
                tax_sum += res_tax.amount
                tax_name = res_tax.code
            annual_tax.append((e.name, tax_name, tax_sum))
            print annual_tax

        docargs = {
            'doc_ids':context['active_ids'],
            'doc_model': model,
            'data': data,
            'docs': docs,
            'company_employees': annual_tax,
            'comp_name': annual_company_id[1],
        }
        return self.env['report'].render('etsi_payroll.report_annual_tax_template', docargs)