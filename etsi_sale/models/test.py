from odoo import fields, models, _api

class LawrenceCute (models.Model):
    _name = 'lawrence.cute'

    name = fields.Char (string="name")