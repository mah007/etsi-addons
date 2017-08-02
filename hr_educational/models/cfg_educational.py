# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EducationalCourses(models.Model):
    _name = 'educational.courses'

    field_of_study = fields.Char(string="Field of Study")
    major = fields.Char(string="Major")
    name = fields.Char(string = "Name")
    description = fields.Char(string = "Description")
