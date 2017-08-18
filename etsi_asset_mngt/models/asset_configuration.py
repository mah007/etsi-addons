from odoo import api, fields, models

class AssetConfiguration(models.Model):
    _name = 'asset.config'

    serial_num = fields.Char(string="Serial #")
    name = fields.Char(string="Asset")
<<<<<<< HEAD
    asset_model = fields.Char(string="Model")
    year = fields.Date(string="Year")
    asset_condition = fields.Selection([('1', 'BRAND NEW'),
                                        ('2', 'USED'),
                                        ('3', 'DAMAGED')],
                                       string="Asset Condition")
    # quantity = fields.Float(string="Quantity")
=======
    asset_model = fields.Many2one('asset.model', string="Model")
    year = fields.Date(string="Year")
    # asset_condition = fields.Selection([('1', 'BRAND NEW'),
    #                                     ('2', 'USED'),
    #                                     ('3', 'DAMAGED')],
    #                                    string="Asset Condition")
    quantity = fields.Integer(string="Quantity")
    asset_wh_ids = fields.One2many('warehouse.config', 'asset_config_id', string="Warehouse")


class WarehouseConfiguration(models.Model):
    _name = 'warehouse.config'

    name = fields.Char(string="Warehouse Name")
    wh_address = fields.Many2one('res.partner', string="Company", domain="[('is_company', '=', True)]")
    assigned_asset_ids = fields.One2many('asset.distribution', 'asset_wh_id', string="Assets")
    asset_config_id = fields.Many2one('asset.config')


class AssetDistribution(models.Model):
    _name = 'asset.distribution'

    asset_id = fields.Many2one('asset.config', string="Asset")
    asset_wh_id = fields.Many2one('warehouse.config', string="Warehouse")
    asset_quantity = fields.Integer(string="Quantity")
    asset_condition = fields.Many2one('asset.condition', string="Asset Condition")
    asset_distribution_date = fields.Date(string="Date")

class AssetModel(models.Model):
    _name = 'asset.model'

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")

class AssetCondition(models.Model):
    _name = 'asset.condition'

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
>>>>>>> 62d37fa05a0155dac51cdd1a7b0e47761ed7157f
