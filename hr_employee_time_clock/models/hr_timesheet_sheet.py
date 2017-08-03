# -*- coding: utf-8 -*-

##############################################################################
#
#    Clear Groups for Odoo
#    Copyright (C) 2016 Bytebrand GmbH (<http://www.bytebrand.net>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    summary_ids = fields.One2many('hr_timesheet.summary', 'sheet_id', string="Timesheet Summary")
    auto_import = fields.Boolean(string="Auto Import")
    auto_overtime = fields.Boolean(string ="Actual Overtime")
    auto_worked_hours = fields.Boolean(string ="Actual Worked Hours")

    @api.onchange('date_from', 'date_to')
    @api.multi
    def change_date(self):
        if self.date_to and self.date_from and self.date_from > self.date_to:
            raise ValidationError(
                _('You added wrong date period.'))

    @api.model
    def create(self, values):
        print 'create'
        if values.get('date_to') and values.get('date_from') \
                and values.get('date_from') > values.get('date_to'):
            raise ValidationError(
                _('You added wrong date period.'))
        if values.get('auto_import'):
            auto_import = True
            self.validate_auto_import(auto_import)

        return super(HrTimesheetSheet, self).create(values)

    @api.multi
    def write(self, values):
        res = super(HrTimesheetSheet, self).write(values)
        if 'auto_import' in values:
            if values['auto_import']:
                auto_import = True
            else:
                auto_import = False
            self.validate_auto_import(auto_import)
        return res



    @api.multi
    def validate_auto_import(self, auto_import):
        for rec in self:
            if auto_import:
                rec.auto_overtime = True
                rec.auto_worked_hours = True
            else:
                rec.auto_overtime = False
                rec.auto_worked_hours = False
        # print 'search', self.env['hr_timesheet.summary'].search([('sheet_id','=',self.id)])
        # self.env['hr_timesheet.summary'].search([('sheet_id','=',self.id)]).sudo().unlink()




class HrTimesheetSummary(models.Model):
    _name = "hr_timesheet.summary"

    employee_id = fields.Many2one('hr.employee', string="Employee", related='sheet_id.employee_id', store=True)
    date = fields.Date(string="Date")
    duty_hours = fields.Float(string="Duty Hours", digits=(16,2))
    worked_hours = fields.Float(string="Worked Hours", digits=(16,2))
    diff = fields.Float(string="Difference", digits=(16,2))
    auth_ot = fields.Float(string="Authorized OT", digits=(16,2))
    actual_ot = fields.Float(string="Actual OT", digits=(16,2))
    actual_worked_hours = fields.Float(string="Actual Worked Hours", digits=(16,2))
    sheet_id = fields.Many2one('hr_timesheet_sheet.sheet', string="Sheet ID", ondelete='cascade')








