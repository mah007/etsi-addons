from odoo import api, models


class PayslipReport(models.AbstractModel):
    _name = 'report.hr_payroll.report_payslip'

    @api.model
    def render_html(self, docids, data=None):
        payslips = self.env['hr.payslip'].browse(docids) #return current id that is being use

        for p in payslips:
            payslip_codes = self.env['hr.payslip.line'].search([('slip_id', '=', p.id)])
            total_deduction = 0.00
            grss = 0.00
            net = 0.00
            for e in payslip_codes:
                if e.code == "GROSS":
                    grss = e.total
                if e.code == "NET":
                    net = e.total
            total_deduction = grss - net

        docargs = {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'docs': payslips,
            'data': data,
            'total_deduction': total_deduction,
        }
        return self.env['report'].render('hr_payroll.report_payslip', docargs)
