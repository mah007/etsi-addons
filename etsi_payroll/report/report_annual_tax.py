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

        res_stud = self.env['hr.payslip'].search([('company_id', '=', annual_company_id[0])])

        data.update({'company_employee': res_stud})


        docargs = {
            'doc_ids':context['active_ids'],
            'doc_model': model,
            'data': data,
            'docs': docs,
            # 'comp_name': comp_id[1], #other ways
        }
        return self.env['report'].render('etsi_payroll.report_annual_tax_template', docargs)