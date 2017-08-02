from odoo import fields, models, api


class policy_groups(models.Model):

    _name = 'hr.policy.group'
    _description = 'HR Policy Groups'

    name =  fields.Char('Name',size=128,)
    # contract_ids = fields.One2many('hr.contract','policy_group_id','Contracts',)

class policy_category(models.Model):
    _name = 'hr.policy.category'
    _description = 'HR Policy Groups'

    name = fields.Char(string ="Name")
    code = fields.Char(string="Code")


class Hr_Contract(models.Model):
    _inherit = 'hr.contract'

    policy_id = fields.Many2one('hr.policy.group', string="Policy")
