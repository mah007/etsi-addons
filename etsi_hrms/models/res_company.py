from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    province_id = fields.Many2one('cfg.region.province', string="Province", compute='_ph_compute_address', inverse='_inverse_province_id')
    city_id = fields.Many2one('cfg.province.city', string="City/Municipality", compute='_ph_compute_address', inverse='_inverse_city_id')
    brgy_id = fields.Many2one('cfg.city.barangay', string="Barangay", compute='_ph_compute_address', inverse='_inverse_brgy_id')
    country_name = fields.Char(string="Country Name", related='country_id.name')

    def _ph_compute_address(self):
        for company in self.filtered(lambda company: company.partner_id):
            address_data = company.partner_id.sudo().address_get(adr_pref=['contact'])
            if address_data['contact']:
                partner = company.partner_id.browse(address_data['contact']).sudo()
                company.province_id = partner.province_id
                company.city_id = partner.city_id
                company.brgy_id = partner.brgy_id

    def _inverse_province_id(self):
        for company in self:
            company.partner_id.province_id = company.province_id

    def _inverse_city_id(self):
        for company in self:
            company.partner_id.city_id = company.city_id

    def _inverse_brgy_id(self):
        for company in self:
            company.partner_id.brgy_id = company.brgy_id
