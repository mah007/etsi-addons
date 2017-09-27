from odoo import fields, models, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip.run'

    emp_email = fields.Char(string="Email")

    @api.multi
    def send_mail_template(self):
        # Find the e-mail template
        template = self.env.ref('etsi_bank_advices.example_email_template')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

        check_emp = self.env['hr.payslip'].search([('payslip_run_id', '=', self.id)])

        # emp_emails = []

        for rec in check_emp:
            self.env['mail.template'].browse(template.id).send_mail(rec.id)

        # print 'in', test
        # Send out the e-mail template to the user



