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
        res_comp = self.env['hr.contract'].search([('partner_id', '=', annual_company_id[0])])

        exemp = 0.00
        annual_tax = []
        for e in res_comp:
            print e.employee_id
            yr_start = datetime.strptime(year_selection, '%Y').date()
            yr_end = date(yr_start.year, 12, 31)
            res_payroll = self.env['hr.payslip.line'].search([('employee_id', '=', e.employee_id.id),
                                                              ('slip_id.state', '=', 'done'),
                                                              ('slip_id.date_from', '>=', yr_start),
                                                              ('slip_id.date_to', '<=', yr_end)])
            tax_name = ' '
            tax_sum = 0
            tax_refund = 0.0
            tax_due = 0.0
            grss = 0.0
            sss = 0.0
            phealth = 0.0
            pgibig = 0.0
            ntax = 0.0
            for r in res_payroll:
                if r.code == 'TAX':
                    tax_sum += r.amount
                    tax_name = r.code
                if r.code == 'GROSS':
                    grss += r.amount
                if r.code == 'SSS':
                    sss += r.amount
                if r.code == 'PHILHEALTH':
                    phealth += r.amount
                if r.code == 'PAGIBIG':
                    pgibig += r.amount
                if r.code == 'OINTAX':
                    ntax += r.amount

            total_deduc = grss - (sss + phealth + pgibig + ntax)
            res_tax_exemp = self.env['payroll.tax.due.status'].search([('tax_stat_code', '=', e.employee_id.tin_type.stat_code)])
            for ex in res_tax_exemp:
                exemp = ex.personal_exemp + ex.additional_exemp

            net_taxable_comp = total_deduc - exemp

            res_tax_due = self.env['payroll.tax.due'].search([('range_min', '<', net_taxable_comp),
                                                             ('range_max', '>=', net_taxable_comp)])
            for t in res_tax_due:
                tax_due = t.tax_due_amount + ((net_taxable_comp - t.excess)*t.rate)

                tax_refund = tax_due - tax_sum

            if res_payroll:
                if net_taxable_comp < 0:
                    net_taxable_comp = 0.0
                else:
                    net_taxable_comp = net_taxable_comp
                if tax_refund < 0:
                    tax_refund = 0.0
                else:
                    tax_refund = tax_refund

                annual_tax.append((e.employee_id.name, tax_name, tax_sum, total_deduc, net_taxable_comp, tax_due, tax_refund))


        docargs = {
            'doc_ids':context['active_ids'],
            'doc_model': model,
            'data': data,
            'docs': docs,
            'company_employees': annual_tax,
            'company_name': annual_company_id,
            'company_date': year_selection,


        }
        return self.env['report'].render('etsi_payroll.report_annual_tax_template', docargs)