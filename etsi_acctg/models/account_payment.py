from odoo import models, fields, api, _
from odoo . exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit ='account.payment'

    @api.multi
    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', 'in', self.ids)],
            'target': 'new',
        }
    @api.multi
    def button_invoices(self):
        return {
            'name': _('Paid Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.invoice_ids])],
            'target':'new',
    }



    @api.multi
    def get_check_voucher_sequence(self, compny_id):
        res_seq = self.env['ir.sequence'].search([('is_checkvoucher','=',True),('partner_id', '=', compny_id)])

        if res_seq:
            code = res_seq.code
            sequence = self.env['ir.sequence'].next_by_code(code)

        else:
            raise ValidationError("No Sequence created for the assigned company")

        return sequence
        print 'seq', sequence

    # @api.multi
    # def create_voucher(self):


    # @api.multi
    # def print_checks(self):
    #     """ Check that the recordset is valid, set the payments state to sent and call print_checks() """
    #     # Since this method can be called via a client_action_multi, we need to make sure the received records are what we expect
    #     self = self.filtered(lambda r: r.payment_method_id.code == 'check_printing' and r.state != 'reconciled')
    #
    #     if len(self) == 0:
    #         raise UserError(_("Payments to print as a checks must have 'Check' selected as payment method and "
    #                           "not have already been reconciled"))
    #     if any(payment.journal_id != self[0].journal_id for payment in self):
    #         raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))
    #
    #     if not self[0].journal_id.check_manual_sequencing:
    #         # The wizard asks for the number printed on the first pre-printed check
    #         # so payments are attributed the number of the check the'll be printed on.
    #         last_printed_check = self.search([
    #             ('journal_id', '=', self[0].journal_id.id),
    #             ('check_number', '!=', 0)], order="check_number desc", limit=1)
    #         next_check_number = last_printed_check and last_printed_check.check_number + 1 or 1
    #         return {
    #             'name': _('Print Pre-numbered Checks'),
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'print.prenumbered.checks',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'target': 'new',
    #             'context': {
    #                 'payment_ids': self.ids,
    #                 'default_next_check_number': next_check_number,
    #             }
    #         }
    #     else:
    #         self.filtered(lambda r: r.state == 'draft').post()
    #         # return self.do_print_checks()
    #         return self.env['report'].get_action(self, 'etsi_acctg.report_account_payment')

    @api.multi
    def do_print_checks(self):
        data = {}

        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['next_check_number'])[0]
        return self.env['report'].sudo().get_action(self, 'etsi_acctg.report_account_payment_template', data=data)

    def create_voucher(self):
        data = {}

        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        # data['form'] = self.read(['next_check_number'])[0]
        # print 'data_form', data['form']
        return self.env['report'].sudo().get_action(self, 'etsi_acctg.report_voucher_template', data=data)



class CheckVoucherSequence(models.Model):
    _inherit ='ir.sequence'

    @api.model
    def default_get(self, fields):
        context = self.env.context
        result = super(CheckVoucherSequence, self).default_get(fields)
        print 'context', context
        if context:
            if 'check_voucher' in context:
                if context['check_voucher']:
                    result['is_checkvoucher'] = True
        return result

    partner_id = fields.Many2one('res.partner', string='Company')
    is_checkvoucher = fields.Boolean(string='Check Voucher')

    _sql_constraints = [
        ('unique_code', 'unique (code)', "The sequence code must be unique")]
