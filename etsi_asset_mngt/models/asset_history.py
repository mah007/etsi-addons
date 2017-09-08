from odoo import api, fields, models

class AssetManagementHistory(models.Model):
    _name = 'asset.management.history'

    handover_no = fields.Char(string="Handover No")
    serial_number_id = fields.Many2one('account.asset.asset.line', string="Serial Number")
    date_handover = fields.Date(String="Date Handover")
    issuer_name = fields.Many2one('hr.employee',string="Issuer Name")
    recipient_name = fields.Many2one('hr.employee',string="Recipient Name")
    approved_by = fields.Many2one('hr.employee',string="Approved by")
    date_return = fields.Date(string="Date Return")
    # return_issuer_name_id = fields.Many2one('', string="Returner Name")
    received_by_name_id = fields.Many2one('hr.employee', string="Received")

    asset_id = fields.Many2one('account.asset.asset', string="Asset")
    # asset_handover_id = fields.Many2one('asset.management.handover')
    asset_handover_id = fields.Many2one('asset.management.handover',ondelete="cascade")

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    # serial_no_id = fields.Char(string="asfd")
    serial_no_id = fields.Many2one('account.asset.asset.line',string="Choose Serial Number")
    asset_history_ids = fields.One2many('asset.management.history', 'asset_id', string="Asset History")

    # @api.onchange('serial_no_id')
    # def onchange_serial_no_id(self):
    #     # serial_no_line = self.env['account.asset.asset.line'].search([('name', '=', self.serial_no_id.id)])
    #     # print serial_no_line.id
    #     history = self.env['asset.management.history'].search([('serial_number_id', '=', self.serial_no_id.id)])
    #     print history
    #     self.asset_history_ids = history

    def select_serial(self):
        history = self.env['asset.management.history'].search([('serial_number_id', '=', self.serial_no_id.id)])
        print history
        self.asset_history_ids = history