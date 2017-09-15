from odoo import models, fields, api, exceptions
import xmlrpclib

class Delivery(models.Model):
    _name = 'client.delivery'

    name = fields.Char(string="Name",default='Name')
    customer_name =  fields.Char(string='Customer',default='Customer Name')
    customer_address =  fields.Char(string='Address',default='Customer Address')
    source =  fields.Char(string='Source Document',default='Source')
    item_ids = fields.One2many('item.delivery','id_id', string="Items")
    sale_order_id = fields.Integer()
    sent_state = fields.Boolean()
    website_url = fields.Char()
    website_db = fields.Char()
    website_username = fields.Char()
    website_password = fields.Char()

    @api.multi
    def package_sent(self):
        for stock in self:
            if stock.sent_state != True:
                try:

                    url = stock.website_url
                    db = stock.website_db
                    username = stock.website_username
                    password = stock.website_password
                    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
                    vVersion = common.version()
                    uid = common.authenticate(db, username, password, {})
                    print uid
                    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
                    for item in stock.item_ids:
                        item_id = models.execute_kw(db, uid, password, 'stock.pack.operation', 'write', [[item.stock_picking_id],
                            {
                                'qty_done': item.ordered_qty,
                            }])

                    trans_id = models.execute_kw(db, uid, password, 'stock.picking', 'write',[[stock.sale_order_id],
                        {
                            'state': 'done',
                        }])


                except Exception:
                    raise exceptions.ValidationError(
                        'The Website You Are Reaching Is Currently Down Or Under Maintenance')
                stock.sent_state = True
            else:
                raise exceptions.ValidationError('Item/s Has Already Been Mark As Done')