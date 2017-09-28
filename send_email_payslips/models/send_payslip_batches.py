from odoo import fields, models, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip.run'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('close', 'Close'),
        ('sent', 'Sent'),
    ], default='draft')

    @api.multi
    def send_mail_template(self):
        # self.state = 'sent'
        # Find the e-mail template
        template = self.env.ref('send_email_payslips.example_email_template')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

        check_emp = self.env['hr.payslip'].search([('payslip_run_id', '=', self.id)])

        for rec in check_emp:
            self.env['mail.template'].browse(template.id).send_mail(rec.id)
            print '>', rec.employee_id.work_email


