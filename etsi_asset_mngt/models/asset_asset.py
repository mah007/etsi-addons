from odoo import api, fields, models

class AccountAssetAssetLine(models.Model):
    _name = 'account.asset.asset.line'
    # _rec_name = 'serial_no'

    serial_no_id = fields.Many2one('account.asset.asset',string="Serial Number")
    name = fields.Char(string="Serial Number")
    asset_serial_state = fields.Boolean(string="Asset State", default=True) #<<

    _sql_constraints = [
        ('name', 'unique(name)', "Serial number already exists with this asset!"),
    ]

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    serial_no_ids = fields.One2many('account.asset.asset.line', 'serial_no_id', string="Serial Number")
    asset_name = fields.Char (sting = "Asset Name", required = True)
    model_id = fields.Char(string="Model", required = True)

    @api.model
    def create(self, vals):
        if vals['asset_name']:
            asset_name = vals['asset_name']
        else:
            asset_name = ''

        if vals['model_id']:
            model_id = vals['model_id']
        else:
            model_id = ''

        name = "{}-{}".format(asset_name, model_id)

        print 'name', name
        print 'asset name', asset_name
        vals['name'] = name
        vals['asset_name'] = asset_name
        vals['model_id'] = model_id

        return super(AccountAssetAsset, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'asset_name' in vals:
            if vals['asset_name']:
                asset_name = vals['asset_name']
        else:
            asset_name = self.asset_name

        if 'model_id' in vals:
            if vals['model_id']:
                model_id = vals['model_id']
        else:
            model_id = self.model_id

        name = "{}-{}".format(asset_name, model_id)

        print 'name', name
        print 'asset name', asset_name
        print 'model id', model_id
        vals['name'] = name
        vals['asset_name'] = asset_name
        vals['model_id'] = model_id

        return super(AccountAssetAsset, self).write(vals)