from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _

class Hr_Holidays(models.Model):
    _inherit = 'hr.holidays'

    # state = fields.Selection(selection_add=[('cancel', 'Cancelled')])
    req_cancel = fields.Boolean(string="Request to Cancel")
    cancel_reason = fields.Text(string="Reason for Cancellation")
    can_req_cancel = fields.Boolean("Can Request Cancel", compute='_compute_can_cancel')

    @api.multi
    def action_request_cancel(self):
        # return self.write({'req_cancel': True})

        context = {'leave_id':self.id}
        print 'context', context
        return {
            'view_mode': 'form',
            'res_model': 'holidays.cancellation',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            'context': context,
            'name': 'Leave Cancellation'
        }

    @api.multi
    def action_cancel(self):
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            # if holiday.state == 'validate1':
            #     holiday.write({'state': 'refuse', 'manager_id': manager.id})
            # else:
            #     holiday.write({'state': 'refuse', 'manager_id2': manager.id})
            # # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()

        if self.payslip_status == False:
            self.state = 'cancel'
            self._remove_resource_leave()
        else:
            raise ValidationError(_('Cannot cancel request. Leave has been reported to last payslip'))
        return

    @api.multi
    def action_refuse_cancel(self):
        self.req_cancel = False
        return

    @api.multi
    def _compute_can_cancel(self):
        """ User can request to cancel a leave request if it is its own leave request
            or if he is an Hr Manager.
        """
        user = self.env.user
        group_hr_manager = self.env.ref('hr_holidays.group_hr_holidays_manager')
        for holiday in self:
            if holiday.type != 'add':
                if holiday.state in ('validate', 'validate1') and holiday.req_cancel == False:
                    if group_hr_manager in user.groups_id or holiday.employee_id and holiday.employee_id.user_id == user:
                        holiday.can_req_cancel = True


    @api.multi
    def action_draft(self):
        for holiday in self:
            if not holiday.can_reset:
                raise UserError(_('Only an HR Manager or the concerned employee can reset to draft.'))
            if holiday.state not in ['confirm', 'refuse']:
                raise UserError(_('Leave request state must be "Refused" or "To Approve" in order to reset to Draft.'))
            holiday.write({
                'state': 'draft',
                'manager_id': False,
                'manager_id2': False,
                'req_cancel': False,
            })
            linked_requests = holiday.mapped('linked_request_ids')
            for linked_request in linked_requests:
                linked_request.action_draft()
            linked_requests.unlink()
        return True

class HolidaysCancellation(models.Model):
    _name = 'holidays.cancellation'
    _description = 'Holidays Cancellation'

    reason = fields.Text(string='Reason')


    @api.multi
    def action_save(self):
        context = self.env.context
        if context:
            if 'leave_id' in context:
                if context['leave_id']:
                    leave_id = context['leave_id']
                    leave_obj = self.env['hr.holidays'].browse(leave_id)
                    leave_obj.sudo().write({'cancel_reason':self.reason,'req_cancel':True})
        return True






