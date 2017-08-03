from odoo import models, fields, api

class Partner(models.Model):
    _inherit ='res.partner'

    first_name = fields.Char(String="First Name")
    middle_name = fields.Char(String="Middle Name")
    last_name = fields.Char(String="Last Name")
    age = fields.Integer(string='Age', compute='_compute_age')
    prefix = fields.Many2one('res.partner.title', 'Prefix')
    suffix = fields.Selection([('jr', 'Jr'),
                               ('sr', 'Sr'),
                               ('ii', 'II'),
                               ('iii', 'III'),
                               ('iv', 'IV')], string="Suffix")
    address_type = fields.Selection([('1', 'Current'),
                                     ('2', 'Permanent'),
                                     ('3', 'Office'),
                                     ('4', 'Mailing')], string="Address Type")

    @api.model
    def create(self, vals):
        fnct_type = 'create'
        empinfo = self.get_emp_name(vals, fnct_type)
        vals['first_name'] = empinfo['fname']
        vals['middle_name'] = empinfo['mname']
        vals['last_name'] = empinfo['lname']
        if 'first_name' in vals or 'middle_name' in vals or 'last_name' in vals:
            if vals['first_name'] or vals['middle_name'] or vals['last_name']:
                vals['name'] = empinfo['name']
        else:
            vals['name'] = vals['name']




        return super(Partner, self).create(vals)

    @api.multi
    def write(self, vals):
        fnct_type = 'write'
        empinfo = self.get_emp_name(vals, fnct_type)
        vals['first_name'] = empinfo['fname']
        vals['middle_name'] = empinfo['mname']
        vals['last_name'] = empinfo['lname']


        if 'first_name' in vals or 'middle_name' in vals or 'last_name' in vals:
            if vals['first_name'] or vals['middle_name'] or vals['last_name']:
                vals['name'] = empinfo['name']
        else:
            vals['name'] = self.name

        return super(Partner, self).write(vals)

    @api.onchange('first_name', 'middle_name', 'last_name')
    def onchange_first_name(self):
        fnct_type = 'onchange'
        vals = {'first_name': self.first_name,
                'middle_name': self.middle_name,
                'last_name': self.last_name
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


        # name = lname + ', ' + fname + ' ' + mname + ' ' + suffix
        name = "{}, {} {}".format(lname, fname, mname)
        values = {
            'fname': fname,
            'mname': mname,
            'lname': lname,
            'name': name,
        }
        return values
