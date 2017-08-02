# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date

class Employee(models.Model):
    _inherit = 'hr.employee'

    first_name = fields.Char(String="First Name")
    middle_name = fields.Char(String="Middle Name")
    last_name = fields.Char(String="Last Name")
    age = fields.Integer(string='Age',compute='_compute_age')
    prefix = fields.Many2one('res.partner.title', 'Prefix')
    suffix = fields.Selection([('jr', 'Jr'),
                               ('sr', 'Sr'),
                               ('ii', 'II'),
                               ('iii', 'III'),
                               ('iv', 'IV')], string="Suffix")
    marital = fields.Selection(selection_add=[("separated","Separated")])
    street = fields.Text(string="Street", related='address_home_id.complete_address')
    province_id = fields.Many2one('cfg.region.province', string="Province", related='address_home_id.province_id')
    city_id = fields.Many2one('cfg.province.city', string="City/Municipality", related='address_home_id.city_id')
    brgy_id = fields.Many2one('cfg.city.barangay', string="Barangay", related='address_home_id.brgy_id')
    zip = fields.Char(string="Zip Code", related='address_home_id.zip')
    philhealth = fields.Char(string="Philhealth")
    sss = fields.Char(string="SSS No")
    tin = fields.Char(string="TIN No")
    wage = fields.Float(string="Wage", digits=(16,2))
    pay_type = fields.Char(string="Pay Type")
    schedule_pay = fields.Char(string="Pay Freq")
    biometric_num = fields.Char(string="Biometric No.")
    emp_categ_id = fields.Many2one('hr.employee.category', string="Employee Category", help="For Employee Identifaction Number Purposes")


    @api.model
    def default_get(self, fields):
        result = super(Employee, self).default_get(fields)
        ph_id = self.env.ref('base.ph').id
        if ph_id:
            result['country_id'] = ph_id
            result['category_ids'] = [self.env.ref('etsi_hrms.hr_emp_categ_regular').id]
        return result

    @api.model
    def create(self, vals):
        fnct_type = 'create'
        empinfo = self.get_emp_name(vals, fnct_type)
        vals['first_name'] = empinfo['fname']
        vals['middle_name'] = empinfo['mname']
        vals['last_name'] = empinfo['lname']

        # vals['name'] = empinfo['name']
        if 'first_name' in vals or 'middle_name' in vals or 'last_name' in vals:
            if vals['first_name'] or vals['middle_name'] or vals['last_name']:
                vals['name'] = empinfo['name']
        else:
            vals['name'] = vals['name']

        if 'name' in vals and 'birthday' in vals:
            self.check_name_exist(vals['name'] ,vals['birthday'])

        if 'emp_categ_id' in vals:
            if vals['emp_categ_id']:
                identification_id = self.get_emp_sequence(vals['emp_categ_id'])
                vals['identification_id'] = identification_id



        return super(Employee, self).create(vals)

    @api.multi
    def write(self, vals):
        fnct_type = 'write'
        empinfo = self.get_emp_name(vals, fnct_type)
        vals['first_name'] = empinfo['fname']
        vals['middle_name'] = empinfo['mname']
        vals['last_name'] = empinfo['lname']

        if 'birthday' in vals:
            bday = vals['birthday']
        else:
            bday = self.birthday

        # vals['name'] = empinfo['name']

        if 'first_name' in vals or 'middle_name' in vals or 'last_name' in vals:
            if vals['first_name'] or vals['middle_name'] or vals['last_name']:
                vals['name'] = empinfo['name']
        else:
            vals['name'] = self.name

        if 'name' in vals:
            self.check_name_exist(vals['name'], bday)

        return super(Employee, self).write(vals)


    @api.multi
    def get_emp_sequence(self, emp_categ_id):
        sequence_obj = self.env['ir.sequence'].search(
            [('is_employee', '=', True), ('emp_categ_id', '=', emp_categ_id), ('active', '=', True)])
        if sequence_obj:
            code = sequence_obj.code
            sequence = self.env['ir.sequence'].next_by_code(code)
        else:
            raise ValidationError('No series created for the Assigned Company')
        return sequence

    @api.multi
    def copy(self, default=None):
        raise UserError(_('You cannot duplicate Employee.'))

    @api.multi
    @api.depends('birthday')
    def _compute_age(self):
        for record in self:
            if record.birthday:
                record.age = relativedelta(
                    fields.Date.from_string(fields.Date.today()),
                    fields.Date.from_string(record.birthday)).years
            else:
                record.age = 0


    @api.multi
    def check_name_exist(self,name,bday):
        if self:
            res = self.search([('name', '=', name), ('birthday', '=', bday),('id','!=', self.id)])
        else:
            res = self.search([('name', '=', name), ('birthday', '=', bday)])
        if res:
            raise ValidationError('Record Already Exist. Please Review Employee Name and B-day Info')


    @api.onchange('first_name','middle_name','last_name')
    def onchange_first_name(self):
        fnct_type = 'onchange'
        vals = {'first_name':self.first_name,
                'middle_name':self.middle_name,
                'last_name':self.last_name
                }
        empinfo = self.get_emp_name(vals, fnct_type)

        self.name = empinfo['name']

    @api.multi
    def get_emp_name(self, values, fnct_type):
        if 'first_name' in values and values['first_name']:
            fname = values['first_name'].title().strip()
        elif fnct_type == 'write' and 'first_name' not in values and self.first_name:
            fname = self.first_name.title().strip()
        else:
            fname = ''

        if 'middle_name' in values and values['middle_name']:
            mname = values['middle_name'].title().strip()
        elif fnct_type == 'write' and 'middle_name' not in values and self.middle_name:
            mname = self.middle_name.title().strip()
        else:
            mname = ''

        if 'last_name' in values and values['last_name']:
            lname = values['last_name'].title().strip()
        elif fnct_type == 'write' and 'last_name' not in values and self.last_name:
            lname = self.last_name.title().strip()
        else:
            lname = ''

        if 'suffix' in values and values['suffix']:
            suffix = values['suffix']
        elif fnct_type == 'write' and 'suffix' not in values and self.suffix:
            suffix = self.suffix
        else:
            suffix = ''

        if suffix:
            suffix = self._get_emp_suffix(suffix)

        # name = lname + ', ' + fname + ' ' + mname + ' ' + suffix
        name = "{}, {} {} {}".format(lname, fname, mname, suffix)
        values = {
            'fname':fname,
            'mname':mname,
            'lname':lname,
            'name':name,
        }
        return values

    @api.multi
    def _get_emp_suffix(self, val):
        if val == 'jr':
            suffix = 'Jr'
        elif val == 'ii':
            suffix = 'II'
        elif val == 'iii':
            suffix = 'III'
        elif val == 'iv':
            suffix = 'IV'
        else:
            suffix = ''

        return suffix


    @api.onchange('country_id')
    def onchange_country_id(self):
        self.province_id = False
        self.city_id = False
        self.brgy_id = False
        self.zip = False
        country_id = self.country_id.id
        res_region = self.env['cfg.country.region'].search([('country_id', '=', country_id)])
        region_ids = []
        for region_id in res_region:
            region_ids.append(region_id.id)

        return {'domain': {'province_id': [('region_id', 'in', region_ids)]}, }

    @api.onchange('province_id')
    def onchange_province_id(self):
        self.city_id = False
        self.brgy_id = False
        self.zip = False
        province_id = self.province_id.id
        return {'domain': {'city_id': [('province_id', '=', province_id)]}, }

    @api.onchange('city_id')
    def onchange_city_id(self):
        self.brgy_id = False
        self.zip = False
        city_id = self.city_id.id
        return {'domain': {'brgy_id': [('city_id', '=', city_id)]}, }

class Department(models.Model):
    _inherit = 'hr.department'
    _order = 'parent_id,name'


class EmployeeSequence(models.Model):
    _inherit = 'ir.sequence'

    is_employee = fields.Boolean(string="Employee")
    emp_categ_id = fields.Many2one('hr.employee.category', string="Employee Category")
