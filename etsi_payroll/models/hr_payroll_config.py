from odoo import models, fields, api

class Payroll_SSS_Matrix(models.Model):
    _name = 'payroll.sss.matrix'
    _description = 'SSS Contribution table'

    sal_range_min = fields.Float(string="Minimum Salary")
    sal_range_max = fields.Float(string="Maximum Salary")
    employer_share = fields.Float(string="Employer Share")
    employee_share = fields.Float(string="Employee Share")
    employer_compensation = fields.Float(string="Employer Compensation")
    # total_contribution = fields.Float(string="Total Contribution", compute ='_get_total')
    total_contribution = fields.Float(string="Total Contribution")

    # @api.depends('employer_share','employee_share','employer_compensation')
    # def _get_total(self):
    #     total = self.employer_share + self.employer_compensation + self.employee_share
    #     print '>>',total

class Payroll_PhilHealth_Matrix(models.Model):
    _name = 'payroll.philhealth.matrix'
    _description = 'Philhealth Contribution table'

    sal_range_min = fields.Float(string="Minimum Salary")
    sal_range_max = fields.Float(string="Maximum Salary")
    employer_share = fields.Float(string="Employer Share")
    employee_share = fields.Float(string="Employee Share")
    total_monthly_premium = fields.Float(string="Total Monthly Premiun")

class Payroll_Pagibig_Matrix(models.Model):
    _name = 'payroll.pagibig.matrix'
    _description = 'Pag-ibig Contribution table'

    sal_range_min = fields.Float(string="Minimum Salary Range")
    sal_range_max = fields.Float(string="Maximum Salary Range")
    employer_share = fields.Float(string="Employer Share(%)")
    employee_share = fields.Float(string="Employee Share(%)")
    total = fields.Float(string="Total Monthly Contribution")

class Payroll_Tax_Period(models.Model):
    _name = 'payroll.tax.period'
    _description = 'Tax Period'

    period_code = fields.Char(string="Code")
    name = fields.Char(string="Description")

class Payroll_Tax_Status(models.Model):
    _name = 'payroll.tax.status'
    _description = 'Tax Status'

    stat_code = fields.Char(string="Code")
    name = fields.Char(string="Description")

class Payroll_Tax_Exemption(models.Model):
    _name = 'payroll.tax.exemption'
    _description = 'Tax Exemption'

    name = fields.Char(string="Name")
    period_ids = fields.Many2one('payroll.tax.period',string="Period")
    col_num = fields.Integer(string="Column Number")
    tax_value = fields.Float(string="Exemption")
    tax_rate = fields.Float(string="Rate(%)")


class Payroll_Tax_Income_Range(models.Model):
    _name = 'payroll.tax.income.range'
    _description = 'Tax Income Range'

    exemp_ids = fields.Many2one('payroll.tax.exemption', string="Exemption Column")
    period_ids = fields.Many2one('payroll.tax.period',string="Period")
    stat_ids = fields.Many2one('payroll.tax.status', string="Status")
    income_min = fields.Float(string="Minimum Income")
    income_max = fields.Float(string="Maximum Income")

class Payroll_Tax_Due(models.Model):
    _name = 'payroll.tax.due'
    _description = 'Annual Tax Due'

    range_min = fields.Float(string="Over")
    range_max = fields.Float(string="But not Over")
    tax_due_amount = fields.Float(string="Amount")
    rate = fields.Float(string="Rate(%)")
    excess = fields.Float(string="of Excess Over")

class Payroll_Tax_Due_Status(models.Model):
    _name = 'payroll.tax.due.status'
    _description = 'Tax Due Status'

    tax_stat_code = fields.Char(string="Code")
    personal_exemp = fields.Float(string="Personal Exemption")
    additional_exemp = fields.Float(string="Additional Exemption")

# class Payroll_OT_Day_Type(models.Model):
#     _name = 'payroll.ot.day.type'
#     _description = 'Payroll Overtime Day Type'
#
#     name = fields.Char(string="Name")
#     active = fields.Boolean(string="Active", default=True)
#
# class Payroll_OT_Rate(models.Model):
#     _name = 'payroll.ot.rate'
#     _description = 'Payroll Ovetime Rate'
#
#     name = fields.Char(string="Name")
#     ot_day_type = fields.Many2one('payroll.ot.day.type', string="Overtime Type")
#     rate = fields.Integer(string="Rate(%)")
#
#     @api.multi
#     def name_get(self):
#         res = []
#         for record in self:
#             name = record.ot_day_type.name
#             res.append((record.id, name))
#         return res



