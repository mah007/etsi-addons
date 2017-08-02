from odoo import api, models, fields

class Institution(models.Model):
    _inherit = 'res.partner'

    is_institution = fields.Boolean(string="Institution")

