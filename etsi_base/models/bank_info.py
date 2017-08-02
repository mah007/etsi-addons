import re

from odoo import api, fields, models
from odoo.osv import expression

from odoo import fields, models, api

class Res_Bank(models.Model):
    _inherit ='res.bank'

    short_name = fields.Char(string="Short Name")
    branch_ids = fields.One2many('res.bank.branch', 'bank_id', string="Branches")


class Res_Bank_Branch(models.Model):
    _name = 'res.bank.branch'

    name = fields.Char(string="Branch Name")
    br_code = fields.Char(string="Code")
    bank_id = fields.Many2one('res.bank', string="Bank")
    region_id = fields.Many2one('cfg.country.region', string="Region")
    province_id = fields.Many2one('cfg.region.province', string="Province")
    city_id = fields.Many2one('cfg.province.city', string="Minicipality/City")
    brgy_id = fields.Many2one('cfg.city.barangay', string="Barangay")
    street = fields.Char(string="Street")
    phone = fields.Integer(string="Phone")
    email = fields.Char(string="Email")
    active = fields.Boolean(string="Active", default=True)


class BankAccount(models.Model):
    _inherit = 'res.partner.bank'
    branch_id = fields.Many2one('res.bank.branch', string="Branch")
    acc_name = fields.Char(string="Account name")
    acc_type = fields.Selection([('savings','Savings Account'),('current','Current Account'),('atm','ATM')], string="Account Type")
    active = fields.Boolean('Active', default=False)


    @api.onchange('bank_id')
    def onchange_bank_id(self):
        self.branch_id = False
        return {'domain': {'branch_id': [('bank_id', '=', self.bank_id.id)]}, }
