# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EducFieldStudy(models.Model):
    _name = 'educ.fields.study'

    name = fields.Char(string = "Name")
    description = fields.Char(string = "Description")
