from odoo import fields, api, models

class Employee (models.Model):
    _inherit = 'hr.employee'

    government_ids = fields.One2many ('hr.government.ids', 'government_id', string = "Governemt IDS")

class GovernmentIDS (models.Model):
    _name = 'hr.government.ids'

    number = fields.Char(string = "Number")
    date_issued = fields.Date (string = "Date issued")

    government_type_id = fields.Many2one ('cfg.government.id.type', string = "Government ID Types")
    government_id = fields.Many2one ('hr.employee', string = "Government IDS")