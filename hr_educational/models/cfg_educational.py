# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EducationalCourses(models.Model):
    _name = 'educational.courses'

    field_of_study = fields.Many2one('educ.fields.study', string="Field of Study")
    major = fields.Char(string="Major")

class EducFieldStudy(models.Model):
    _name = 'educ.fields.study'

    name = fields.Char(string = "Name")
    description = fields.Char(string = "Description")