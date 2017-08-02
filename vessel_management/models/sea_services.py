
from odoo import api, fields, models
from datetime import datetime, timedelta


class SeaServices(models.Model):
    _name = "sea.services"
    _description = "Sea Services"
    _inherit = ['mail.thread']

    def _get_years(self):
        this_year = datetime.today().year

        results = [(str(x), str(x)) for x in range(this_year - 40, this_year + 10)]
        return results

    name = fields.Char(string="Name")
    vessel_id = fields.Many2one('vessel.management', string="Vessel")
    type_id = fields.Many2one('vessel.type', string="Type", related='vessel_id.type_id')
    gross_weight = fields.Float(string="GRT", related="vessel_id.gross_weight")
    dead_weight = fields.Float(string="DWT", related="vessel_id.dead_weight")
    engine_id = fields.Many2one('vessel.engine' ,string="Engine", related="vessel_id.engine_id")
    year_built = fields.Selection(_get_years,string="Year Built", related="vessel_id.year_built")
    sign_on = fields.Date(string="Sign On")
    sign_off = fields.Date(string="Sign Off")
    duration = fields.Char(string="Duration")
    fleet_mngr = fields.Many2one('res.partner', string="Fleet Manager", related="vessel_id.fleet_mngr")
    manning_agency = fields.Many2one('res.partner', string="Manning Agency", related="vessel_id.manning_agency")
    emp_id = fields.Many2one('hr.employee', string ="Employee ID")

class Hr_Employee(models.Model):
    _inherit='hr.employee'

    sea_services_ids = fields.One2many('sea.services',
                                       'emp_id',
                                       string='Sea Services')
