from odoo import models, fields, api, exceptions

class Item(models.Model):
    _name = 'item.delivery'

    name = fields.Char(string="Name",default='Name')
    ordered_qty =  fields.Char(string='Quantity',default='Quantity')
    id_id = fields.Many2one('client.delivery', string="ID")
    stock_picking_id = fields.Integer()