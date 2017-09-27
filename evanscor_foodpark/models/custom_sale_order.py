from odoo import fields,api,models,exceptions
import xmlrpclib

class CustomSaleOrder(models.Model):
    _inherit = 'stock.picking'

    sent_state = fields.Boolean()

    @api.multi
    def send_packaging(self):
        for stock in self:
            if stock.sent_state != True:
                try:

                    url = 'http://192.168.1.37:8069'
                    db = 'Flexerp'
                    username = 'admin'
                    password = 'admin'
                    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
                    vVersion = common.version()
                    uid = common.authenticate(db, username, password, {})
                    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

                    client_id = models.execute_kw(db, uid, password, 'client.delivery', 'create', [
                        {'name': stock.name,
                         'customer_name': stock.partner_id.name,
                         'customer_address': stock.partner_id.street,
                         'source': stock.origin,
                         'sale_order_id': stock.id,
                         'website_url': 'http://localhost:8069',
                         'website_db': 'Website_FoodPark',
                         'website_username': 'admin',
                         'website_password': 'admin',
                         }])
                    for item in stock.pack_operation_product_ids:
                        print item.id
                        item_id = models.execute_kw(db, uid, password, 'item.delivery', 'create', [
                            {
                                'name': item.product_id.name,
                                'ordered_qty': item.ordered_qty,
                                'id_id': client_id,
                                'stock_picking_id': item.id
                            }])

                except Exception:
                    raise exceptions.ValidationError('The Website You Are Reaching Is Currently Down Or Under Maintenance')
                stock.sent_state = True
            else:
                raise exceptions.ValidationError('Item/s Has Already Been Sent')


