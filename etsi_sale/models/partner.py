# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleCustomer(models.Model):
    _inherit = 'res.partner'


    dti_num = fields.Integer(string="DTI No")
    sec_num = fields.Integer(string="SEC No")
    cdc_num = fields.Integer(string="CDC No")
    sub_cap = fields.Integer(string="Subscribe Capital")
    paid_cap = fields.Integer(string="Paid Capital")

    bod_id = fields.Many2one('res.partner')
    bod_ids = fields.One2many('res.partner','bod_id', string="Board of Directors", domain=[('is_company', '=', False)])
    cus_id = fields.Many2one('res.partner')
    cus_ids = fields.One2many('res.partner','bod_id', string="Customer", domain=[('customer', '=', True)])
    sup_id = fields.Many2one('res.partner')
    sup_ids = fields.One2many('res.partner','bod_id', string="Supplier", domain=[('supplier', '=', True)])

    comp_type = fields.Selection([
        ('1', 'Sole Proprietor'),
        ('2', 'Partnership'),
        ('3', 'Corporation'),
        ('4', 'Cooperative'),
        ], 'Company Type',)

