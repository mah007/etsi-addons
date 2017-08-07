from odoo import models, fields, api

class HrPolicyOt(models.Model):
    _name = 'hr.policy.ot'
    _description = 'Overtime Policy'
    _order = 'date desc'

    name = fields.Char(string="Name", required=True)
    date = fields.Date(string="Effective Date", required=True)
    line_ids =fields.One2many('hr.policy.line.ot','policy_id',string="Policy Lines")
    policy_categ = fields.Many2one('hr.policy.category', string="Policy for")

    @api.onchange('policy_categ')
    def _onchange_policy_categ(self):
        if self.policy_categ:
            self.name = self.policy_categ.name
        else:
            self.name = ""

    @api.model
    def create(self, vals):
        policy_categ = self.env['hr.policy.category'].search([('id', '=', vals['policy_categ'])])

        vals['name'] = policy_categ.name

        return super(HrPolicyOt, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'policy_categ' in vals:
            policy_categ = self.env['hr.policy.category'].search([('id', '=', vals['policy_categ'])])
            print policy_categ.name
            vals['name'] = unicode(policy_categ.name)

        res_id = super(HrPolicyOt, self).write(vals)
        return res_id

class HrPolicyLineOt(models.Model):
    _name = 'hr.policy.line.ot'
    _description = 'Overtime Policy Line'

    name = fields.Char(string="Name", required=True)
    policy_id = fields.Many2one('hr.overtime.policy',string='Policy')
    type = fields.Selection([('daily', 'Ordinary'),
                             ('restday', 'Rest Day'),
                             ('holiday', 'Public Holiday'),
                             ('rest_on_holiday', 'Holiday on Restday')],
                            string="Type", required=True)
    weekly_working_days = fields.Integer(string="Weekly Working Days")
    # active_after = fields.Float(string="Active After",help="Minutes after which this policy applies")
    active_start_time = fields.Float(string="Active Start Time", help="Time in 24 hour time format")
    active_end_time = fields.Float(string="Active End Time", help="Time in 24 hour time format")
    rate = fields.Float(string="Rate(%)", required=True, help='Multiplier of employee wage.')
    code = fields.Char(string="Code", required=True, help="Use this code in the salary rules.")
    holiday_id = fields.Many2one('hr.holidays.public.type', string="Holiday Type")

class policy_group(models.Model):
    _name = 'hr.policy.group'
    _inherit = 'hr.policy.group'


    ot_policy_ids = fields.Many2many('hr.policy.ot', 'hr_policy_group_ot_rel','group_id', 'ot_id', 'Overtime Policy')
