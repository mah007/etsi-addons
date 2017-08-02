from odoo import fields, models, api
from datetime import datetime, timedelta

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    in_house = fields.Boolean(string="Employee")
    seaman = fields.Boolean(string="Seaman")
    allottee_ids = fields.One2many(
        'employee.allottee','emp_ids',
        string='Allotment Payee'
    )
    status = fields.Selection([('onboard','On Board'),('offboard','Off Board')], string="Status", default='offboard')

    @api.model
    def default_get(self, fields):
        context = self.env.context
        result = super(HrEmployee, self).default_get(fields)

        if context:
            if 'emp_type' in context:
                if context['emp_type'] == 'seaman':
                    result['seaman'] = True
                    result['in_house'] = False
                    result['category_ids'] = [self.env.ref('vessel_management.seaman_categ_employee').id]
                elif context['emp_type'] == 'in_house':
                    result['seaman'] = False
                    result['in_house'] = True
                    result['category_ids'] = [self.env.ref('etsi_hrms.hr_emp_categ_regular').id]
        return result

    @api.onchange('category_ids')
    def onchange_category_ids(self):
        categ_ids = []
        category_ids = self.category_ids
        for categ in category_ids:
            categ_ids.append(categ.id)

        seaman_id = self.env.ref('vessel_management.seaman_categ_employee').id
        if seaman_id in categ_ids:
            self.seaman = True
    @api.multi
    def act_sign_off(self):
        self.status = 'offboard'

    @api.multi
    def act_sign_on(self):
        # for rec in self:
        #     rec.status = 'onboard'
        context = {'emp_id': self.id}
        print 'context', context
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sign_on.management',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            'context': context
        }

class Employee_Allottee(models.Model):
    _name = 'employee.allottee'

    # name = fields.Many2many('res.partner', 'employee_allottee_rel', 'emp_id', 'partner_id', 'Allottee')
    partner_id = fields.Many2one('res.partner',string='Allottee', domain=[('is_allottee', '=', True),('is_company', '=', False)])
    allottee_type = fields.Selection([('primary','Primary'),
                                      ('secondary', 'Secondary'),
                                      ('tertiary', 'Tertiary')],
                                     string="Allottee Type")
    percentage = fields.Float(string="Allotment Percentage")
    relationship = fields.Selection([('mother', 'Mother'),
                                     ('father','Father'),
                                     ('sister','Sister'),
                                     ('wife','Wife'),
                                     ('co-partner','Common Law Partner'),
                                     ('fiance','Fiance')],
                                    string="Relationship")
    emp_ids = fields.Many2one('hr.employee',string="Employee")
    payslip_id = fields.Many2one('hr.payslip', string="payslip")