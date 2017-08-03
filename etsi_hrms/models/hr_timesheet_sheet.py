import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.tools.sql import drop_view_if_exists
from odoo.exceptions import UserError, ValidationError


class HrTimesheetSheet(models.Model):
    _inherit =  "hr_timesheet_sheet.sheet"

    def _default_date_from(self):
        user = self.env['res.users'].browse(self.env.uid)
        r = user.company_id and user.company_id.timesheet_range or 'month'
        if r == 'month':
            return time.strftime('%Y-%m-01')
        elif r == 'week':
            return (datetime.today() + relativedelta(weekday=0, days=-6)).strftime('%Y-%m-%d')
        elif r == 'year':
            return time.strftime('%Y-01-01')
        return fields.Date.context_today(self)

    def _default_date_to(self):
        user = self.env['res.users'].browse(self.env.uid)
        r = user.company_id and user.company_id.timesheet_range or 'month'
        if r == 'month':
            return (datetime.today() + relativedelta(months=+1, day=1, days=-1)).strftime('%Y-%m-%d')
        elif r == 'week':
            return (datetime.today() + relativedelta(weekday=6)).strftime('%Y-%m-%d')
        elif r == 'year':
            return time.strftime('%Y-12-31')
        return fields.Date.context_today(self)

    # date_from = fields.Date(string='Date From', default=_default_date_from, required=True,
    #                         index=True, readonly=True, states={'new': [('readonly', False)]})
    # date_to = fields.Date(string='Date To', default=_default_date_to, required=True,
    #                       index=True, readonly=True, states={'new': [('readonly', False)]})

    # set the state condition when draft, date_from and date_to will be editable not only in NEW state (refer above code)

    date_from = fields.Date(string='Date From', default=_default_date_from, required=True,
                            index=True,readonly=True, states={'draft': [('readonly', False)],'new': [('readonly', False)]})
    date_to = fields.Date(string='Date To', default=_default_date_to, required=True,
                          index=True, readonly=True, states={'draft': [('readonly', False)],'new': [('readonly', False)]})
