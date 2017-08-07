
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

class Contribution_Register_Report(models.AbstractModel):
    _inherit = 'report.hr_payroll.report_contributionregister'


    @api.model
    def render_html(self, docids, data=None):
        register_ids = self.env.context.get('active_ids', [])
        contrib_registers = self.env['hr.contribution.register'].browse(register_ids)
        date_from = data['form'].get('date_from', fields.Date.today())
        date_to = data['form'].get('date_to', str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10])
        # get_code = self._get_payslip_lines(register_ids)
        _code = self.env['hr.payslip.line'].search([('register_id','=',register_ids)])
        _data_from = datetime.strptime(date_from, "%Y-%m-%d")
        _data_to = datetime.strptime(date_to, "%Y-%m-%d")
        _date_from = _data_from.strftime("%m-%d-%Y")
        _date_to =_data_to.strftime("%m-%d-%Y")
        # print 'contrib_registers', _code
        lines_data = self._get_payslip_lines(register_ids, date_from, date_to)
        # _code = get_code.code
        # lines_data = self._get_payslip_lines(register_ids, _date_from, _date_to)
        lines_total = {}
        lines_total_emplyr = {}
        for register in contrib_registers:
            lines = lines_data.get(register.id)
            lines_total[register.id] = lines and sum(lines.mapped('total')) or 0.00
            lines_total_emplyr[register.id] = lines and sum(lines.mapped('employer_share')) or 0.00
        docargs = {
            'doc_ids': register_ids,
            'doc_model': 'hr.contribution.register',
            'docs': contrib_registers,
            'data': data,
            # 'code': _code,
            'date_from': _date_from,
            'date_to': _date_to,
            'lines_data': lines_data,
            'code': _code[0].code,
            'lines_total': lines_total,
            'lines_total_emplyr': lines_total_emplyr,
        }
        return self.env['report'].render('hr_payroll.report_contributionregister', docargs)

