from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('semi-monthly', 'Semi-Monthly'),
    ], string='Scheduled Pay', index=True, default='monthly')

    # schedule_pay = fields.Selection([
    #     ('monthly', 'Monthly'),
    #     ('quarterly', 'Quarterly'),
    #     ('semi-annually', 'Semi-annually'),
    #     ('annually', 'Annually'),
    #     ('weekly', 'Weekly'),
    #     ('bi-weekly', 'Bi-weekly'),
    #     ('bi-monthly', 'Bi-monthly'),
    # ], string='Payroll Frequency', index=True, default='monthly')
    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ], 'Day of Week', required=True, index=True, default='0')
    # value_1 = fields.Integer(string="1st Value")
    # value_2 = fields.Integer(string="2nd Value")
    # value_1 = fields.Boolean(string="1st Pay")
    # value_2 = fields.Boolean(string="2nd Pay")

    value = fields.Selection([('first','First Pay'),
                              ('second', 'Second Pay')], string = 'Pay when')

    sss_contri = fields.Boolean(string="SSS",default=True)
    philhealth_contri = fields.Boolean(string="Philhealth",default=True)
    pagibig_contri = fields.Boolean(string="Pagibig",default=True)
