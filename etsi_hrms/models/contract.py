from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Contract(models.Model):
    _inherit = 'hr.contract'

    partner_id = fields.Many2one('res.partner', string="Assigned to(Company)")
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('pending', 'To Renew'),
        ('terminate','Pre-terminate'),
        ('close', 'Expired'),
    ], string='Status', track_visibility='onchange', help='Status of the contract', default='draft')

    @api.model
    def create(self, vals):
        if vals['partner_id']:
            vals['name'] = self.get_sequence(vals['partner_id'])
        return super(Contract, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'partner_id' in vals:
            self.name = self.get_sequence(vals['partner_id'])
        return super(Contract, self).write(vals)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            active_contract = self.search([('employee_id', '=', self.employee_id.id),('state','in',('draft','open','pending'))])
            if active_contract:
                raise ValidationError('An active contract exist with this employee')
            else:
                application_id = self.employee_id.application_id
                wage = 0
                contract = self.search([('employee_id', '=', self.employee_id.id)])
                if len(contract) <= 0:
                    if application_id:
                        wage = application_id.salary_proposed

                self.job_id = self.employee_id.job_id
                self.department_id = self.employee_id.department_id
                self.wage = wage
                self.partner_id = application_id.assigned_partner_id or False


    @api.multi
    def get_sequence(self, partner_id):
        sequence_obj = self.env['ir.sequence'].search([('contract', '=', True), ('partner_id', '=', partner_id),('active','=',True)])
        if sequence_obj:
            code = sequence_obj.code
            sequence = self.env['ir.sequence'].next_by_code(code)
        else:
            raise ValidationError('No series created for the Assigned Company')
        return sequence

    @api.multi
    def set_as_terminate(self):
        return self.write({'state': 'terminate'})




class Employee(models.Model):
    _inherit = 'hr.employee'

    application_id = fields.Many2one('hr.applicant', string="Application")


    # payroll_type = fields.Selection([('daily', 'Daily'),('monthly','Monthly')], string="Payroll Type")

#     @api.model
#     def create(self, vals):
#         res = super(Contract, self).create(vals)
#         if vals['employee_id']:
#             employee_id = self.env['hr.employee'].browse(vals['employee_id'])
#             if vals['wage']:
#                 employee_id.write({'wage': vals['wage']})
#             # if vals['schedule_pay']:
#             #     print 'sched_pay', vals['schedule_pay']
#             #     employee_id.write({'schedule_pay': str(vals['schedule_pay'])})
#             # if vals['payroll_type']:
#             #     employee_id.write({'pay_type': str(vals['payroll_type'])})
#         return res
#
#     @api.multi
#     def write(self, vals):
#         res =super (Contract, self).write(vals)
#         if self.employee_id:
#             if self.wage:
#                 self.employee_id.write({'wage': self.wage})
#             # if self.schedule_pay:
#             #     print 'sched_pay',self.schedule_pay
#             #     self.employee_id.write({'schedule_pay': str(self.schedule_pay)})
#             # if self.payroll_type:
#             #     self.employee_id.write({'pay_type': str(self.payroll_type)})
#         return res
# #

class ContractSequence(models.Model):
    _inherit = 'ir.sequence'

    partner_id = fields.Many2one('res.partner', string="Company")
    contract = fields.Boolean(string="Contract")

    _sql_constraints = [
        ('code', 'unique (code)', 'Sequence code must be unique!'),
    ]

    @api.model
    def default_get(self, fields):
        context = self.env.context
        result = super(ContractSequence, self).default_get(fields)
        if context:
            if 'contract' in context:
                if context['contract'] == True:
                    result['contract'] = True

        return result

    @api.model
    def create(self, vals):
        context = self.env.context
        if 'contract' in context:
            if context['contract']:
                if vals['partner_id']:
                    self.check_company_exists(vals['partner_id'])
        return super(ContractSequence, self).create(vals)

    @api.multi
    def write(self, vals):
        context = self.env.context
        if 'contract' in context:
            if context['contract']:
                if 'partner_id' in vals:
                    if vals['partner_id']:
                        self.check_company_exists(vals['partner_id'])
        return super(ContractSequence, self).write(vals)

    @api.multi
    def check_company_exists(self, partner_id):
        res = self.search([('contract', '=', True), ('active', '=', True), ('partner_id', '=', partner_id)])
        if res:
            partner_obj = self.env['res.partner'].browse(partner_id)
            partner_name = partner_obj.name
            raise ValidationError("Series for %s already exists" % partner_name)







