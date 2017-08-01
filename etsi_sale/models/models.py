<<<<<<< HEAD
#american cream.py
=======
# -*- coding: utf-8 -*-

from odoo import models, fields, api

#Lawrence sobrang cute
#test
#wag babasahin, ang kulet binabasa mo pa din eh
class etsi_sale(models.Model):
    _name = 'etsi_sale.etsi_sale'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=False)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        self.value2 = float(self.value) / 100

#aksjgjklf
>>>>>>> c42a84c7516a41f4091e576f5afe6ba96fd61a71
vnvb
dsadasczxcasdsac