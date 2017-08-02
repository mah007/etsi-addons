from odoo import models, fields, api

class AddressType(models.Model):
    _inherit = 'res.partner'

    address_type = fields.Selection([('1', 'Current Address'),
                                  ('2', 'Permanent Address'),
                                  ('3', 'Office Address'),
                                  ('4', 'Mailing')], string="Address Type")