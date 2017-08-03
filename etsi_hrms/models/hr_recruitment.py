from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
import re

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    @api.multi
    def _validate_email(self):
        for partner in self:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", partner.email_from) == None:
                return False
        return True

    partner_mobile = fields.Char("Mobile", size=11)
    first_name = fields.Char(String="First Name")
    middle_name = fields.Char(String="Middle Name")
    last_name = fields.Char(String="Last Name")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="Start Date")
    assigned_partner_id = fields.Many2one('res.partner', string="Assigned to(Company)")


    _constraints = [
        (_validate_email, 'Please enter a valid email address.', ['email_from']),
    ]

    @api.constrains('partner_mobile')
    def _check_partner_mobile(self):
        if len(self.partner_mobile) <> 11:
            raise ValidationError(_('Please enter valid Mobile number'))

    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            address_id = contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({'application_id':applicant.id,
                                                           'name': applicant.partner_name or contact_name,
                                                           'first_name': applicant.first_name or False,
                                                           'middle_name': applicant.middle_name or False,
                                                           'last_name': applicant.last_name or False,
                                                           'job_id': applicant.job_id.id,
                                                           'address_home_id': address_id,
                                                           'h_street': applicant.partner_id.complete_address or False,
                                                           'h_province_id': applicant.partner_id.province_id.id or False,
                                                           'h_city_id': applicant.partner_id.city_id.id or False,
                                                           'h_brgy_id': applicant.partner_id.brgy_id.id or False,
                                                           'h_zip': applicant.partner_id.zip or False,
                                                           'department_id': applicant.department_id.id or False,
                                                           'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                                                           'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
                                                           'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False})
                applicant.write({'emp_id': employee.id})
                applicant.job_id.message_post(
                    body=_(
                        'New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
                employee._broadcast_welcome()

            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window['res_id'] = employee.id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window
