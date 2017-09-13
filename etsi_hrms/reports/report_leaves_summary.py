import pytz

from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ReportLeavesSummary(models.AbstractModel):
    _name = 'report.etsi_hrms.report_leaves_summary'

    @api.model
    def render_html(self, docids, data={}):
        dtf = DEFAULT_SERVER_DATETIME_FORMAT
        context = dict(self.env.context or {})
        data = data if data is not None else {}
        model = context.get('active_model') or context.get('model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        print 'employee', docs.employee
        print 'FROM', docs.from_date
        print 'TO', docs.to_date

        # if docs.from_date and docs.to_date:
        #
        #     date_from = datetime.strftime(datetime.strptime(docs.from_date,'%Y-%m-%d',),'%Y-%m-%d')
        #     print 'date_from', date_from
        #     res_holidays = self.env['hr.holidays'].search([('employee_id', '=', docs.employee[0].id)])
        #     if res_holidays:
        #         res_holidays.filtered(lambda r: datetime.strftime(pytz.utc.localize(datetime.strptime(r.date_from, dtf)).astimezone(local),'%Y-%m-%d') == get_date)


        leaves = []

        leaves_allocation = self.env['hr.holidays'].search([('employee_id', '=', docs.employee.id)])

        total_leaves = 0
        total_removes = 0

        for rec in leaves_allocation:
            if rec.type == 'add':
                total_leaves += rec.number_of_days
            else:
                total_removes -= rec.number_of_days

        total_remaining = total_leaves - total_removes

        print total_remaining
        print total_leaves
        print total_removes


        data.update({'emp': leaves})

        docargs = {
            'doc_ids': docids,
            'doc_model': 'hr.holidays',
            'docs': docs,
            'data': data,
            # 'leaves': leaves,
            'tot_leaves': total_leaves,
            'tot_removes': total_removes,
            'tot_remaining': total_remaining,
        }
        return self.env['report'].render('etsi_hrms.report_leaves_summary', docargs)