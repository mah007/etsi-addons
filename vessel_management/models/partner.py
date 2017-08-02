from odoo import fields, models, api

class Partner(models.Model):
    _inherit ='res.partner'

    first_name = fields.Char(string="Firstname")
    last_name = fields.Char(string="Lastname")
    middle_name = fields.Char(string="Middlename")
    prefix = fields.Selection([('mr','Mr.'),
                               ('ms', 'Ms.'),
                               ('mrs', 'Mrs.')],
                              string="Prefix")
    suffix = fields.Selection([('sr','Sr.'),
                               ('jr', 'Jr.'),
                               ('i', 'I'),
                               ('ii', 'II'),
                               ('iii', 'III'),
                               ('iv', 'IV'),
                               ('v', 'V'),],
                              string="Suffix")
    status = fields.Selection([('draft','Draft'),
                              ('active', 'Active'),
                              ('inactive', 'Inactive'),
                              ('onhold', 'onhold')],
                             string="Status",
                             default="draft")
    is_allottee = fields.Boolean(string="Is Allottee")
    is_manning_agncy = fields.Boolean(string="Manning")
    is_fleet_mngr = fields.Boolean(string="Fleet Manager")
    is_ship_owner = fields.Boolean(string="Ship Owner")

    @api.model
    def default_get(self, fields):
        result = super(Partner, self).default_get(fields)
        context = self.env.context
        if context:
            print 'context', context
            if 'is_allottee' in context:
                if context['is_allottee']:
                    result['is_allottee'] = True
            if 'is_manning_agncy' in context:
                if context['is_manning_agncy']:
                    result['is_manning_agncy'] = True
            if 'is_fleet_mngr' in context:
                if context['is_fleet_mngr']:
                    result['is_fleet_mngr'] = True
            if 'is_ship_owner' in context:
                if context['is_ship_owner']:
                    result['is_ship_owner'] = True
        return result

    @api.depends('is_company')
    def _compute_company_type(self):
        context = self.env.context
        print 'context', context
        for partner in self:
            print 'company_type', partner.company_type
            if 'is_allottee' in context:
                if context['is_allottee']:
                    partner.company_type = 'person'
            elif 'is_manning_agncy' in context:
                if context['is_manning_agncy']:
                    partner.company_type = 'company'
            elif 'is_fleet_mngr' in context:
                if context['is_fleet_mngr']:
                    partner.company_type = 'company'
            elif 'is_ship_owner' in context:
                if context['is_ship_owner']:
                    partner.company_type = 'company'
            else:
                partner.company_type = 'company' if partner.is_company else 'person'

    @api.onchange('first_name', 'middle_name', 'last_name','is_allottee')
    def onchange_first_name(self):
        if self.is_allottee == True:
            fnct_type = 'onchange'
            vals = {'first_name': self.first_name,
                    'middle_name': self.middle_name,
                    'last_name': self.last_name
                    }
            empinfo = self.get_emp_name(vals, fnct_type)

            self.name = empinfo['name']

    @api.multi
    def get_emp_name(self, values, fnct_type):
        if self.is_allottee == True:

            if 'first_name' in values and values['first_name']:
                fname = values['first_name'].title()
            elif fnct_type == 'write' and 'first_name' not in values and self.first_name:
                fname = self.first_name.title()
            else:
                fname = ''

            if 'middle_name' in values and values['middle_name']:
                mname = values['middle_name'].title()
            elif fnct_type == 'write' and 'middle_name' not in values and self.middle_name:
                mname = self.middle_name.title()
            else:
                mname = ''

            if 'last_name' in values and values['last_name']:
                lname = values['last_name'].title()
            elif fnct_type == 'write' and 'last_name' not in values and self.last_name:
                lname = self.last_name.title()
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

            name = lname + ', ' + fname + ' ' + mname + ' ' + suffix
            values = {
                'fname': fname,
                'mname': mname,
                'lname': lname,
                'name': name,
            }
        return values




