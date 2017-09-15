from odoo import api, fields, models

class AssetHistoryReport(models.AbstractModel):
    _name = 'report.etsi_asset_mngt.asset_history_temp'
    # _inherit = 'account.asset.asset'
    @api.multi
    def render_html(self, docids, data={}):
        data = data if data is not None else {}
        docs = self.env['account.asset.asset'].browse(docids)
        # print self.asset_name
        if docs.serial_no_id:
            asset_history_id = self.env['asset.management.history'].search([('serial_number_id', '=', docs.serial_no_id.id)])
        else:
            asset_history_id = self.env['asset.management.history'].search([('asset_id', '=', docs.id)])


        docargs = {
            'doc_ids': docids,
            'doc_mode': 'account.asset.asset',
            'docs': docs,
            'asset_history_id': asset_history_id,
        }
        return self.env['report'].render('etsi_asset_mngt.asset_history_temp', docargs)