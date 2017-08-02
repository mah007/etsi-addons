from odoo import fields, models, api
from datetime import datetime, timedelta, date

class Remittance_Advice(models.Model):
    _name = 'remittance.advice'
    _description ='Remittance Advice'
    _order = "date desc"

    name = fields.Many2one('res.partner', string="Name", domain=[('is_company', '=', True)], required=True)
    remit_no = fields.Integer(string="Remittance No.")
    remitter_bank = fields.Many2one('res.bank', string="Bank", domain=[('is_foreign', '=', True)])
    date = fields.Date(string="Date", default=date.today())
    amount = fields.Float(string="Amount", required=True)
    currency_id = fields.Many2one('res.currency', string="Currency")
    beneficiary_id = fields.Many2one('res.partner', string="Name", required=True, domain=[('is_company', '=', True)])
    bank_id = fields.Many2one('res.bank', string="Bank")
    branch_id = fields.Many2one('res.bank.branch', string="Bank Branch")
    account_no = fields.Integer(string="Account No.")
    account_name = fields.Char(string="Account Name")
    rate = fields.Float(string="Fx Rate", required=True,digits =(16,2))
    local_amount = fields.Float(string="Amount(Php)", store=True, compute='_compute_local_amount')
    remarks =fields.Text(string="Remarks")

    @api.depends('rate','amount')
    def _compute_local_amount(self):
        self.local_amount = self.amount * self.rate

    @api.onchange('beneficiary_id')
    def _onchange_beneficiary(self):
        s_beneficiary = self.beneficiary_id

        partner_bank = self.env['res.partner.bank'].search([('partner_id', '=', s_beneficiary.id),('active', '=',True)])
        self.bank_id = partner_bank.bank_id
        self.branch_id = partner_bank.branch_id
        self.account_no = partner_bank.acc_number
        self.account_name = partner_bank.acc_name

    @api.model
    def create(self, vals):
        s_beneficiary = vals['beneficiary_id']

        partner_bank = self.env['res.partner.bank'].search([('partner_id', '=', s_beneficiary),('active', '=',True)])

        vals['bank_id'] = partner_bank.bank_id.id
        vals['branch_id'] = partner_bank.branch_id.id
        vals['account_no'] = partner_bank.acc_number
        vals['account_name'] = partner_bank.acc_name

        return super(Remittance_Advice, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'beneficiary_id' in vals:
            s_beneficiary = vals['beneficiary_id']

            partner_bank = self.env['res.partner.bank'].search([('partner_id', '=', s_beneficiary)])

            vals['bank_id'] = partner_bank.bank_id.id
            vals['branch_id'] = partner_bank.branch_id.id
            vals['account_no'] = partner_bank.acc_number
            vals['account_name'] = partner_bank.acc_name

        res = super(Remittance_Advice, self).write(vals)
        return res

    class Res_Bank(models.Model):
        _inherit = 'res.bank'

        is_foreign = fields.Boolean(string="Is Foreign")
