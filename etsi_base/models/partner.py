# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class git/etsi-addons/etsi_base(models.Model):
#     _name = 'git/etsi-addons/etsi_base.git/etsi-addons/etsi_base'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

# -*- coding: utf-8 -*-


class Partner(models.Model):
    _inherit ='res.partner'


    first_name = fields.Char(string="First name")
    last_name = fields.Char(string="Last name")
    middle_name = fields.Char(string="Middle name")

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

    @api.model
    def create(self, vals,):
        if vals['first_name']:
            first_name = vals['first_name'].title()
        else:
            first_name = ''

        if vals['last_name']:
            last_name = vals['last_name'].title()
        else:
            last_name = ''

        if vals['middle_name']:
            middle_name = vals['middle_name'].title()
        else:
            middle_name = ''


        name = "{}, {} {} ".format(last_name, first_name, middle_name)
        print 'name', name
        vals['name'] = name
        vals['first_name'] = first_name
        vals['middle_name'] = middle_name
        vals['last_name'] = last_name

        return super(Partner, self).create(vals)

    @api.multi
    def write(self, vals,):
        if 'first_name' in vals:
            if vals['first_name']:
                first_name = vals['first_name'].title()
        else:
            first_name = self.first_name.title()

        if 'middle_name' in vals:
            middle_name = vals['middle_name'].title()
        else:
            middle_name = self.middle_name.title()

        if 'last_name' in vals:
            last_name = vals['last_name'].title()
        else:
            last_name = self.last_name.title()

        name = "{}, {} {} ".format(last_name, first_name, middle_name)
        print 'name', name
        vals['name'] = name
        vals['first_name'] = first_name
        vals['middle_name'] = middle_name
        vals['last_name'] = last_name

        return super(Partner, self).write(vals)