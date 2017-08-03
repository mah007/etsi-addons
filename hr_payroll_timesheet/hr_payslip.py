# -*- coding: utf-8 -*-
from openerp import models, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):

        def create_empty_worked_lines(employee_id, contract_id, date_from, date_to):
            attendance = {
                'name': 'Timesheet Attendance',
                'sequence': 10,
                'code': 'ATTN',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract_id,
            }

            overtime = {
                'name': 'Timesheet Overtime',
                'sequence': 11,
                'code': 'OT',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract_id,
            }

            valid_days = [
                ('sheet_id.employee_id', '=', employee_id),
                ('sheet_id.state', '=', 'done'),
                ('sheet_id.date_from', '>=', date_from),
                ('sheet_id.date_to', '<=', date_to),
            ]
            return attendance, overtime, valid_days

        attendances = []
        overtimes = []

        for contract in self.env['hr.contract'].browse(contract_ids):
            attendance, overtime, valid_days = create_empty_worked_lines(
                contract.employee_id.id,
                contract.id,
                date_from,
                date_to
            )


            # for day in self.env['hr_timesheet_sheet.sheet.day'].search(valid_days):
            #     if day.total_attendance >= 0.0:
            #         attendance['number_of_days'] += 1
            #         print 'day.total_attendance', day.total_attendance
            #         attendance['number_of_hours'] += day.total_attendance
            #
            # # needed so that the shown hours matches any calculations you use them for
            # attendance['number_of_hours'] = round(attendance['number_of_hours'], 2)
            # attendances.append(attendance)
            for rec in self.env['hr_timesheet.summary'].sudo().search([('employee_id', '=', contract.employee_id.id),
                                                                ('sheet_id.state', '=', 'done'),
                                                                ('date', '>=', date_from),
                                                                ('date', '<=', date_to),]):
                if rec.actual_worked_hours > 0:
                    attendance['number_of_days'] += 1
                    attendance['number_of_hours'] += rec.actual_worked_hours
                if rec.actual_ot > 0:
                    overtime['number_of_days'] += 1
                    overtime['number_of_hours'] += rec.actual_ot
            attendance['number_of_hours'] = round(attendance['number_of_hours'], 2)
            attendances.append(attendance)
            overtime['number_of_hours'] = round(overtime['number_of_hours'], 2)
            overtimes.append(overtime)

            if overtimes[0]['number_of_days']> 0:
                overtimes = overtimes
            else:
                if contract.working_hours.work_type != 'daily':
                    overtimes = []


            if contract.working_hours.work_type == 'daily':
                work_days = attendances + overtimes
            else:
                work_days = super(HrPayslip, self).get_worked_day_lines(contract_ids, date_from, date_to) + attendances + overtimes

            return work_days


