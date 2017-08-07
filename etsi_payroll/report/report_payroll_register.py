import pytz

from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ReportPayrollRegister(models.AbstractModel):
    _name = 'report.etsi_payroll.report_payroll_register'

    def get_timesheets(self, docs):
        df = DEFAULT_SERVER_DATETIME_FORMAT
        user_tz = self.env.user.tz or str(pytz.utc)
        local = pytz.timezone(user_tz)

        print 'from', docs.from_date
        print 'to', docs.to_date
        print 'compnay', docs.company

        date_from = datetime.strptime(docs.from_date, "%m-%d-%Y").date()
        date_to = datetime.strptime(docs.to_date, "%m-%d-%Y").date()


        payslip = self.env['hr.payslip'].search([('company_id','=',docs.company.id),
                                                       ('date_from', '>=', date_from),
                                                       ('date_to', '<=', date_to),
                                                       ('state','=','done')])

        print 'payslips', payslip

        # payslip_list = []
        # for rec in payslip:
        #     payslip_list.append(rec.id)
        #
        #
        # payslip_lines = self.env['hr.payslip.line'].search([('slip_id','in',payslip_list)])
        # print 'payslips', payslip_lines

        record = []
        sum = []; sum_basic = 0; sum_gross = 0; sum_net = 0; sum_abs = 0; sum_ot = 0
        sum_sss =0; sum_pagibig=0; sum_phil=0; sum_tax=0; sum_ointax=0; sum_ca=0; sum_oitax=0; sum_adj=0
        for rec in payslip:
            print 'name', rec.employee_id.name
            basic = 0
            gross = 0
            net = 0
            abs = 0
            ot = 0
            sss = 0
            pagibig = 0
            philhealth = 0
            tax = 0
            ointax =0
            oitax = 0
            ca = 0
            adj = 0
            payslip_lines = self.env['hr.payslip.line'].search([('slip_id', '=', rec.id)])
            for r in payslip_lines:
                if r.code == 'BASIC':
                    basic = r.total
                    sum_basic += basic
                if r.code == 'GROSS':
                    gross = r.total
                    sum_gross += gross
                if r.code == 'NET':
                    net = r.total
                    sum_net += net
                if r.code == 'ABS':
                    abs = r.total
                    sum_abs += abs
                if r.code == 'SSS':
                    sss = r.total
                    sum_sss += sss
                if r.code == 'PHILHEALTH':
                    philhealth = r.total
                    sum_phil += philhealth
                if r.code == 'PAGIBIG':
                    pagibig = r.total
                    sum_pagibig += pagibig
                if r.code == 'CA':
                    ca = r.total
                    sum_ca += ca
                if r.code == 'TAX':
                    tax = r.total
                    sum_tax += tax
                if r.code == 'OT':
                    ot = r.total
                    sum_ot += ot
                if r.code == 'OITax':
                    oitax = r.total
                    sum_oitax += oitax
                if r.code == 'OINTax':
                    ointax = r.total
                    sum_ointax += ointax
                if r.code == 'ADJ':
                    adj = r.total
                    sum_adj += adj

            vals = {'name': r.employee_id.name,
                    'basic': basic,
                    'gross': gross,
                    'net': net,
                    'absent': abs,
                    'overtime':ot,
                    'sss':sss,
                    'philhealth':philhealth,
                    'pagibig':pagibig,
                    'tax':tax,
                    'cash_advance':ca,
                    'other_tax':oitax,
                    'other_ntax':ointax,
                    'adjustment': adj,
                    }
            record.append(vals)
        sums = {'sum_basic': sum_basic,
                'sum_gross': sum_gross,
                'sum_net': sum_net,
                'sum_absent': sum_abs,
                'sum_overtime': sum_ot,
                'sum_sss': sum_sss,
                'sum_philhealth': sum_phil,
                'sum_pagibig': sum_pagibig,
                'sum_tax': sum_tax,
                'sum_cash_advance': sum_ca,
                'sum_other_tax': sum_oitax,
                'sum_other_ntax': sum_ointax,
                'sum_adjustment': sum_adj,
                }
        sum.append(sums)

        return [record,sum]

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        payslip_line = self.get_timesheets(docs)
        period = None
        if docs.from_date and docs.to_date:
            period = "From " + str(docs.from_date) + " To " + str(docs.to_date)
        elif docs.from_date:
            period = "From " + str(docs.from_date)
        elif docs.from_date:
            period = " To " + str(docs.to_date)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'company': docs.company.name,
            'period': period,
            'payslip':payslip_line[0],
            'payslip_sum': payslip_line[1],
        }
        print 'docargs', docargs
        return self.env['report'].render('etsi_payroll.report_payroll_register', docargs)


