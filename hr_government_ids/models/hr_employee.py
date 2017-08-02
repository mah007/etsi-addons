# -*- coding: utf-8 -*-

from odoo import models, fields, api

class GovernmentIDType(models.Model):
    _name = 'cfg.government.id.type'

    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")