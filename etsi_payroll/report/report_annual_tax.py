from odoo import models, fields, api, exceptions
from datetime import datetime, date

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
            else:
                raise exceptions.ValidationError("Invalid Company")
        else:
            raise exceptions.ValidationError("Invalid Company")

        if 'year_selection' in data['form']:
            if data['form']['year_selection']:
                year_selection = data['form']['year_selection']
            else:
                raise exceptions.ValidationError("Invalid Year")
        else:
            raise exceptions.ValidationError("Invalid Year")
        res_comp = self.env['hr.employee'].search([('company_id', '=', annual_company_id[0])])

        taxes_sum = 0.00
        annual_tax = []
        for e in res_comp:
            yr_start = datetime.strptime(year_selection,'%Y').date()
            yr_end = date(yr_start.year, 12, 31)
            res_payroll = self.env['hr.payslip.line'].search([('employee_id', '=', e.id),
                                                              ('code', '=', 'TAX'),
                                                              ('slip_id.state', '=', 'done'),
                                                              ('slip_id.date_from', '>=', yr_start),
                                                              ('slip_id.date_to', '<=', yr_end)])
            tax_sum = 0
            for res_tax in res_payroll:
                tax_sum += res_tax.amount
            if res_payroll:
                annual_tax.append((e.name, res_payroll[0].code, tax_sum))

            taxes_sum += tax_sum

        docargs = {
            'doc_ids':context['active_ids'],
            'doc_model': model,
            'data': data,
            'docs': docs,
            'company_employees': annual_tax,
            'company_name': annual_company_id[1],
            'company_date': year_selection,
            'company_annual_tax': taxes_sum,
        }
        return self.env['report'].render('etsi_payroll.report_annual_tax_template', docargs)