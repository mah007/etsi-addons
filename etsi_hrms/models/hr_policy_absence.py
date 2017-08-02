from odoo import fields, models, api


class policy_absence(models.Model):

    _name = 'hr.policy.absence'
    _order = 'date desc'  # Return records with latest date first


    name = fields.Char('Name', size=128, required=True)
    date =  fields.Date('Effective Date', required=True)
    line_ids =  fields.One2many('hr.policy.line.absence', 'policy_id', 'Policy Lines')
    policy_categ = fields.Many2one('hr.policy.category', string="Policy for")

    @api.onchange('policy_categ')
    def _onchange_policy_categ(self):
        if self.policy_categ:
            self.name = self.policy_categ.name
        else:
            self.name = ""

    @api.model
    def create(self, vals):
        policy_categ = self.env['hr.policy.category'].search([('id', '=', vals['policy_categ'])])

        vals['name'] = policy_categ.name

        return super(policy_absence, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'policy_categ' in vals:
            policy_categ = self.env['hr.policy.category'].search([('id', '=', vals['policy_categ'])])
            print policy_categ.name
            vals['name'] = unicode(policy_categ.name)

        res_id = super(policy_absence, self).write(vals)
        return res_id

    # @api.multi
    # def get_codes(self):
    #
    #     res = []
    #     [res.append(
    #         (line.code, line.name, line.type, line.rate, line.use_awol))
    #      for line in self.browse(cr, uid, idx, context=context).line_ids]
    #     return res
    #
    # def paid_codes(self, cr, uid, idx, context=None):
    #
    #     res = []
    #     [res.append((line.code, line.name))
    #      for line in self.browse(
    #         cr, uid, idx, context=context).line_ids if line.type == 'paid']
    #     return res
    #
    # def unpaid_codes(self, cr, uid, idx, context=None):
    #
    #     res = []
    #     [res.append((line.code, line.name))
    #      for line in self.browse(
    #         cr, uid, idx, context=context
    #     ).line_ids if line.type == 'unpaid']
    #     return res


class policy_line_absence(models.Model):

    _name = 'hr.policy.line.absence'


    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', required=True, help="Use this code in the salary rules.")
    holiday_status_id =  fields.Many2one('hr.holidays.status', 'Leave')
    policy_id = fields.Many2one('hr.policy.absence', 'Policy')
    type = fields.Selection([
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('dock', 'Dock')],
        'Type',
        required=True,
        help="Determines how the absence will be treated in payroll. "
             "The 'Dock Salary' type will deduct money (useful for "
             "salaried employees).")
    rate = fields.Float('Rate', required=True, help='Multiplier of employee wage.')
    use_awol = fields.Boolean('Absent w/o Leave',help='Use this policy to record employee time absence not covered by other leaves.')
    use_late = fields.Boolean(string="Late", help='Use this policy to record employee late')
    use_leave = fields.Boolean(string="Leave")
    use_holiday = fields.Boolean(string="Holiday")
    active_after = fields.Float(string="Grace Period",help='Use 24 hour format HH:MM')
    holiday_id = fields.Many2one('hr.holidays.public.type', string="Holiday Type")
    @api.onchange('holiday_status_id')
    def _onchange_leave(self):
        if self.holiday_status_id:
            self.name = self.holiday_status_id.name
        else:
            self.name = ""

    @api.onchange('holiday_id')
    def _onchange_holiday(self):
        if self.holiday_id:
            self.name = self.holiday_id.name + " Holiday"
        else:
            self.name = ""

    @api.onchange('use_awol')
    def _onchange_awol(self):
        if self.use_awol:
            self.name = "Absent Without Leave"
        else:
            self.name = ""

    @api.onchange('use_late')
    def _onchange_late(self):
        if self.use_late:
            self.name = "Late"
        else:
            self.name = ""


    # @api.model
    # def create(self, vals):
    #     print '>>>>', vals
    #     if vals['use_leave'] == True:
    #         holiday_id = self.env['hr.holidays.status'].search([('id', '=', vals['holiday_status_id'])])
    #         vals['name'] = holiday_id.name
    #
    #     if vals['use_awol'] == True:
    #         vals['name'] = "Absent Without Leave"
    #
    #     if vals['use_late'] == True:
    #          vals['name'] = "Late"
    #
    #     return super(policy_line_absence, self).create(vals)
    #
    # @api.multi
    # def write(self, vals):
    #     print '<<<', vals
    #     if 'holiday_status_id' in vals:
    #         holiday_id = self.env['hr.holidays.status'].search([('id', '=', vals['holiday_status_id'])])
    #         vals['name'] = holiday_id.name
    #
    #     if 'use_awol' in vals:
    #         vals['name'] = "Absent Without Leave"
    #
    #     if 'use_late' in vals:
    #          vals['name'] = "Late"
    #
    #     res_id = super(policy_line_absence, self).write(vals)
    #     return res_id

class policy_group(models.Model):

    _name = 'hr.policy.group'
    _inherit = 'hr.policy.group'

    absence_policy_ids = fields.Many2many('hr.policy.absence', 'hr_policy_group_absence_rel','group_id', 'absence_id', 'Absence Policy')
