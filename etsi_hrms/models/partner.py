from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    complete_address = fields.Text(String="Complete Address")
    province_id = fields.Many2one('cfg.region.province', String="Province")
    city_id = fields.Many2one('cfg.province.city', String="City/Municipality")
    brgy_id = fields.Many2one('cfg.city.barangay')
    short_name = fields.Char(sttring="Short Name")

    @api.model
    def default_get(self, fields):
        result = super(Partner, self).default_get(fields)
        ph_id = self.env.ref('base.ph').id
        if ph_id:
            result['country_id'] = ph_id
        return result

    # @api.multi
    # def write(self, vals):
    #     print 'write'
    #     ph_id = self.env.ref('base.ph').id
    #     vals['country_id'] =  ph_id
    #     return super(Partner,self).write(vals)

    @api.onchange('country_id')
    def onchange_country_id(self):
        self.province_id = False
        self.city_id = False
        self.brgy_id = False
        self.zip = False
        country_id = self.country_id.id
        res_region = self.env['cfg.country.region'].search([('country_id', '=', country_id)])
        region_ids = []
        for region_id in res_region:
            region_ids.append(region_id.id)

        return {'domain': {'province_id': [('region_id', 'in',region_ids )]},}

    @api.onchange('province_id')
    def onchange_province_id(self):
        self.city_id = False
        self.brgy_id = False
        self.zip = False
        province_id = self.province_id.id
        return {'domain': {'city_id': [('province_id', '=', province_id)]},}

    @api.onchange('city_id')
    def onchange_city_id(self):
        self.brgy_id = False
        self.zip = False
        city_id = self.city_id.id
        return {'domain': {'brgy_id': [('city_id', '=', city_id)]},}

    @api.multi
    def _display_address(self, without_company=False):
        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        address_format = self.country_id.address_format or \
                         "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self.country_id.name or '',
            'company_name': self.commercial_company_name or '',
            'complete_address':self.complete_address or '',
            'brgy_name':self.brgy_id.name or '',
            'city_name':self.city_id.name or '',
            'province_name':self.province_id.name or '',

        }
        for field in self._address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        print 'args', args
        return address_format % args



