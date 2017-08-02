from odoo import api, fields, models

class HrAdvantages(models.Model):
    _name  = 'hr.advantages'
    _description =  'HR Advantages'

    name = fields.Char(string="Name")
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")
    advantages_package_ids = fields.One2many('hr.advantages.package','advantages_id', string="Packages")
    jo_signature_ids = fields.One2many('job_offer.signatures', 'advantages_id', string="Signatures")
    note = fields.Text(string="Notes")
    active = fields.Boolean(string="Active", default=True)


class HrAdvantagesPackage(models.Model):
    _name = 'hr.advantages.package'
    _description = 'Hr Advantages Package'

    advantages_id = fields.Many2one('hr.advantages', string="Advantages", ondelete='cascade')
    cfg_package_id = fields.Many2one('cfg.advantages.package', string="Package", required=True)
    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")
    sequence = fields.Integer(string="Sequence", default=10)

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            if rec.cfg_package_id.name:
                result.append((rec.id, '%s' % (rec.cfg_package_id.name)))
        return result


class ConfigPackages(models.Model):
    _name = 'cfg.advantages.package'
    _description = 'Config Advantages Package'

    name = fields.Char(string="Name", required=True)


class JobOfferSignatures(models.Model):
    _name = 'job_offer.signatures'

    name = fields.Char(string="Name")
    employee_ids = fields.Many2many('hr.employee','jo_signature_emp_rel', 'jo_signature_id','employee_id', string="Employee")
    advantages_id = fields.Many2one('hr.advantages', string="Advantages")



class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    advantages_id = fields.Many2one('hr.advantages', string="Advantages")