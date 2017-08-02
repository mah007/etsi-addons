from odoo import api, fields, models

class Country_Region(models.Model):
    _name = 'cfg.country.region'
    _description = 'Country Region - Configuration'
    _inherit = ['mail.thread']
    _mail_post_access = 'read'

    name = fields.Char(String="Name")
    region_code = fields.Char(String="Region Code")
    active = fields.Boolean(String="Active", default=True)
    country_id = fields.Many2one('res.country', String="Country")

    @api.model
    def create(self, vals):
        if vals['name']:
            vals['name'] = vals['name'].title()

        return super(Country_Region, self).create(vals)

    @api.multi
    def write(self, vals):
        print 'vals', vals
        if 'name' in vals:
            if vals['name']:
                vals['name'] = vals['name'].title()
        return super(Country_Region, self).write(vals)

class Region_Province(models.Model):
    _name = 'cfg.region.province'
    _description = 'Region Province - Configuration'
    _inherit = ['mail.thread']
    _mail_post_access = 'read'

    name = fields.Char(String="Name")
    province_code = fields.Char(String="Province Code")
    active = fields.Boolean(String="Active", default=True)
    region_id = fields.Many2one('cfg.country.region', String="Region")

    @api.model
    def create(self, vals):
        if vals['name']:
            vals['name'] = vals['name'].title()

        return super(Region_Province, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            if vals['name']:
                vals['name'] = vals['name'].title()
        return super(Region_Province, self).write(vals)

class Province_City(models.Model):
    _name ='cfg.province.city'
    _description = 'Province City - Configuration'
    _inherit = ['mail.thread']
    _mail_post_access = 'read'

    name = fields.Char(String="Name")
    city_code = fields.Char(String="City/Municipality Code")
    active = fields.Boolean(String="Active", default=True)
    province_id = fields.Many2one('cfg.region.province', String="Province")

    @api.model
    def create(self, vals):
        if vals['name']:
            vals['name'] = vals['name'].title()

        return super(Province_City, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            if vals['name']:
               vals['name'] = vals['name'].title()
        return super(Province_City, self).write(vals)

class City_Barangay(models.Model):
    _name = 'cfg.city.barangay'
    _description = 'City Barangay -Configuration'
    _inherit = ['mail.thread']
    _mail_post_access = 'read'

    name = fields.Char(String="Name")
    brgy_code = fields.Char(String="Barangay Code")
    active = fields.Boolean(String="Active", default=True)
    city_id = fields.Many2one('cfg.province.city', String="City/Municipality")

    @api.model
    def create(self, vals):
        print 'brgy_vals', vals
        if vals['name']:
            vals['name'] = vals['name'].title()
        return super(City_Barangay, self).create(vals)

    @api.multi
    def write(self, vals):
        print 'vals', vals
        if 'name' in vals:
            if vals['name']:
                vals['name'] = vals['name'].title()
        return super(City_Barangay, self).write(vals)


class City_Zip_Code(models.Model):
    _name = 'cfg.city.zipcode'

    name = fields.Char(string='Zip Code')
    desc = fields.Text(string='Description')

    city_id = fields.Many2one('cfg.province.city', string='City')
