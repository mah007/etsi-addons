

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class VesselManagement(models.Model):
    _name = "vessel.management"
    _description = "Vessel Management"
    _inherit = ['mail.thread']

    @api.model
    def _default_image(self):
        image_path = get_module_resource('vessel_management', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    def _get_years(self):
        this_year = datetime.today().year

        results = [(str(x), str(x)) for x in range(this_year - 40, this_year + 10)]
        return results


    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    type_id = fields.Many2one('vessel.type', string="Type")
    gross_weight = fields.Float(string="GRT")
    dead_weight = fields.Float(string="DWT")
    engine_id = fields.Many2one('vessel.engine', string="Engine")
    year_built = fields.Selection(_get_years,string="Year Built")
    year_registration = fields.Selection(_get_years,string="Year of Registration")
    registry_id = fields.Many2one('port.registry', string="Port Registry")
    owner_id = fields.Many2many('res.partner', 'vessel_owner_partner_rel', 'vessel_id','partner_id', string="Owner")
    route_id = fields.Many2one('trade.route', string="Trade Route")
    fleet_mngr = fields.Many2one('res.partner', string="Fleet Manager")
    manning_agency = fields.Many2one('res.partner', string="Manning Agency")
    state = fields.Many2one('vessel.status', string="Status")
    active = fields.Boolean(string="Active", default=True)
    image = fields.Binary("Photo", default=_default_image, attachment=True,
                          help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo", attachment=True,
                                 help="Medium-sized photo of the employee. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized photo", attachment=True,
                                help="Small-sized photo of the employee. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")
    onboard_id = fields.One2many('crew.onboard','vessel_id', 'On Board')


    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(VesselManagement, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(VesselManagement, self).write(vals)


    def generate_crew_on_board(self):
        # employee_ids = []
        # res = self.env['hr.contract'].search([('vessel_id','=',self.id),('sign_on','<=',datetime.now().strftime('%Y-%m-%d'))])
        # for rec in res:
        #     if rec.seaman:
        #         employee_ids.append(rec.employee_id.id)
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'crew.onboard',
            'domain': [
                ('vessel_id', '=', self.id),
            ],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True,
            'name':'Crew on Board'
        }


class CrewOnBoard(models.Model):
    _name = "crew.onboard"
    _description = "Crew On Board"

    name = fields.Char(string="Name")
    vessel_id = fields.Many2one('vessel.management', string="Vessel")
    employee_name = fields.Char(string="Seaman")
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char(string="Last Name")
    contract_name = fields.Char(string="Contract")
    sign_on = fields.Date(string="Sign On Date")
    port_embark = fields.Char(string="Port of Embarkation")
    contract = fields.Text(type="text",string="Contract", readonly=True)

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.employee_name))
        return res

    # @api.multi
    # def act_sign_off(self):
    #     res_contract = self.env['hr.contract'].search([('name', '=', self.contract_name), ('state', '!=', 'close')])[0]
    #     res_contract.employee_id.write({'status':'offboard'})
    #     months = datetime.today().month - datetime.strptime(self.sign_on,'%Y-%m-%d').month
    #     days = datetime.today().day - datetime.strptime(self.sign_on,'%Y-%m-%d').day
    #     print 'days', days
    #     duration = str(months) + ' months, ' + str(days) + ' days'
    #     self.env['sea.services'].create({'emp_id':res_contract.employee_id.id,'vessel_id':self.vessel_id.id,'sign_on':self.sign_on,'sign_off':datetime.now().strftime('%Y-%m-%d'),
    #                                      'duration':duration})
    #     self.unlink()

    @api.multi
    def act_sign_off(self):

        res_cntrct = self.env['hr.contract'].search([('name','=', self.contract_name)])[0]
        emp_id = res_cntrct.employee_id.id

        context = {'emp_id': emp_id,'crew_onboard_id':self.id,'sign_on':self.sign_on}
        print 'context', context
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sign_off.management',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            'context': context
        }


    #
    # @api.onchange('contract_name')
    # def onchange_contract_name(self):
    #     print 'onchange'
    #     self.contract = self._get_contract_display()
    #
    # @api.multi
    # def _get_contract_display(self):
    #     for rec in self:
    #         res_contract = self.env['hr.contract'].search([('name', '=', rec.contract_name), ('state', '!=', 'close')])
    #         job_name = ''
    #         dept_name = ''
    #         vessel = ''
    #         sign_on_date = ''
    #         wage = ''
    #         date_start = ''
    #         date_end = ''
    #         duration = ''
    #         for rec in res_contract:
    #             if rec.job_id:
    #                 job_name = rec.job_id.name
    #             if rec.department_id:
    #                 dept_name = rec.department_id.name
    #             if rec.vessel_id:
    #                 vessel = rec.vessel_id.name
    #             if rec.sign_on:
    #                 sign_on_date = rec.sign_on
    #             if rec.wage:
    #                 wage = rec.wage
    #             if rec.date_start:
    #                 date_start = str(rec.date_start)
    #             if rec.date_end:
    #                 date_start = str(rec.date_end)
    #             duration = date_start + ' - ' + date_end
    #
    #         output = [
    #             '<style>.attendanceTable td,.attendanceTable th {padding: 10px; border: 1px solid #C0C0C0;} </style><table class="attendanceTable" width="80%">']
    #         output.append('<tr>')
    #         output.append('<th style="text-align:center">' + 'RANK' + '</th>')
    #         output.append('<th style="text-align:center">' + 'DEPARTMENT' + '</th>')
    #         output.append('<th style="text-align:center">' + 'VESSEL' + '</th>')
    #         output.append('<th style="text-align:center">' + 'SIGN ON DATE' + '</th>')
    #         output.append('<th style="text-align:center">' + 'WAGE' + '</th>')
    #         output.append('<th style="text-align:center">' + 'DURATION' + '</th>')
    #         output.append('<th style="text-align:center">' + 'MONTHS' + '</th>')
    #         output.append('</tr>')
    #
    #         output.append('<tr>')
    #         output.append('<td style="text-align:center">' + job_name + '</th>')
    #         output.append('<td style="text-align:center">' + dept_name + '</th>')
    #         output.append('<td style="text-align:center">' + vessel + '</th>')
    #         output.append('<td style="text-align:center">' + sign_on_date + '</th>')
    #         output.append('<td style="text-align:center">' + wage + '</th>')
    #         output.append('<td style="text-align:center">' + duration + '</th>')
    #         output.append('</tr>')
    #
    #         output.append('</table>')
    #         print 'output', output
    #         res = '\n'.join(output)
    #         return res