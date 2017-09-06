from odoo import fields, api, models
import psycopg2 as p
import random,os

class BankAdvice(models.Model):
    _name = 'hr.bank.advice'

    name = fields.Many2one('res.partner', string="Company", required=True)
    bank = fields.Many2one('res.bank', string="Bank", required=True)
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    bank_acct = fields.Many2one('res.partner.bank', string="Bank Account", required=True)
    bank_advice_line_ids = fields.One2many('hr.bank.advice.line', 'bank_advice_id', string="Bank Advice Line")
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('closed', "Closed")], default='draft')

    @api.onchange('name')
    def onchange_name(self):
        self.payslip_ids = ''
        self.bank_acct = ''
        self.bank = ''
        selected_name = self.name.id
        bank_account_list = self.env['res.partner.bank'].search([('partner_id','=',selected_name)])
        print bank_account_list
        bank_id_list = []

        for b in bank_account_list:
            bank_id_list.append(b.bank_id.id)

        return {'domain':{'bank':[('id','in',bank_id_list)]},}

    def generate_line(self):
        self.state = 'confirmed'
        selected_name = self.name.id
        date_from = self.date_from
        date_to = self.date_to
        contract = self.env['hr.contract'].search([('partner_id','=',selected_name),('state','!=','close')])
        payslip_lines = self.env['hr.payslip.line'].search([('slip_id.state', '=', 'done'),('slip_id.date_from', '>=', date_from),
                                                            ('slip_id.date_to','<=', date_to)])
        net = 0
        emp_id = 0
        bank_account = 0
        bank = 0
        id_num = 0

        res = self.env['hr.bank.advice.line'].search([('id', '>', 0)])
        for r in res:
            if r.id > id_num:
                id_num = r.id
            else:
                id_num = id_num

        for c in contract:
            for p in payslip_lines:
                if p.code == 'NET' and p.employee_id == c.employee_id:
                    emp_id = p.employee_id.id
                    bank_account = p.employee_id.bank_account_id.id
                    bank = p.employee_id.bank_account_id.bank_id.id
                    net = p.amount
                    self.bank_advice_line_ids.create({
                        'emp_id': emp_id,
                        'bank_account': bank_account,
                        'bank': bank,
                        'salary': net,
                        'date_from': self.date_from,
                        'date_to': self.date_to,
                    })
        res2 = self.env['hr.bank.advice.line'].search([('id', '>', id_num)])
        self.bank_advice_line_ids = res2

    @api.multi
    def send_email(self):
        # Find the e-mail template
        # template = self.env.ref('etsi_payroll.bank_advice_template')
        # You can also find the e-mail template like this:
        template = self.env['ir.model.data'].get_object('etsi_payroll', 'bank_advice_template')

        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.state = 'closed'

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('etsi_payroll', 'bank_advice_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        # user = self.env['res.partner'].browse(1)
        # print user
        ctx = dict()
        ctx.update({
            'default_model': 'hr.bank.advice',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_partner_id':1,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def main_gen(self):
        self.state = 'draft'
        print 'enter success'
        # connection to database
        conn = p.connect(database="Flexerp", user="flexerp", password="flexerp", host="localhost",
                                port="5432")

        # naming/placing/opening of file
        a = random.randint(1, 9999)
        name = 'filename' + str(a * 7) + '.txt'
        textfile = open(name, 'w')
        message = "HELLO WORLD"
        textfile.write(message)
        textfile.close()

        with open(name, 'r') as f_read:
            file_data = f_read.read()
            print 'file_data', file_data

        values = {
            'name': name,
            'datas_fname': name,
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas': file_data.encode('utf8').encode('base64'),
        }
        cur.execute(
            "SELECT hr_employee.name_related, res_partner_bank.acc_number, salary FROM hr_employee, hr_bank_advice_line, res_partner_bank WHERE hr_employee.id = hr_bank_advice_line.emp_id AND res_partner_bank.id = hr_bank_advice_line.bank_account AND bank_advice_id = %s" % self.id)
        rows = cur.fetchall()
        file.write("emp id,bank account id,salary\n")
        rows_count = 0
        total_salary = 0

        attachment_id = self.env['ir.attachment'].sudo().create(values)
        for row in rows:
            file.write('"%s",' % row[0])
            file.write("%s," % row[1])
            file.write("%s\n" % row[2])
            rows_count += 1
            total_salary += row[2]

        # Prepare your download URL
        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }

        file = open(completeName, 'r')
        print file.read()
        file.close()

class HrBankAdviceReport(models.AbstractModel):
    _name = 'report.etsi_payroll.bank_advice_line_report_temp'

    @api.multi
    def render_html(self, docids, data={}):
        data = data if data is not None else {}
        docs = self.env['hr.bank.advice'].browse(docids)
        salary = 0
        bank_advice_line_id = self.env['hr.bank.advice.line'].search([('bank_advice_id','=', docs.id)])
        print 'self.id', self.id
        for s in bank_advice_line_id:
            salary += s.salary
        print 'salary', salary
        docargs = {
            'doc_ids': docids,
            'doc_mode': 'stud_course.professor',
            'docs': docs,
            'total_salary': salary,
        }
        return self.env['report'].render('etsi_payroll.bank_advice_line_report_temp', docargs)

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def send_mail_template(self):
        # Find the e-mail template
        template = self.env.ref('etsi_payroll.example_email_template')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)

class HrBankAdviceLine(models.Model):
    _name = 'hr.bank.advice.line'

    payslip_line = fields.Many2one('hr.payslip.line', string='Payslip Line', store=True)
    emp_id = fields.Many2one('hr.employee', string="Employee Name", store=True)
    bank_account = fields.Many2one('res.partner.bank', string="Bank Account", store=True)
    # bank = fields.Many2one('res.bank', string="Bank", store=True)
    salary = fields.Float(string="Salary")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    bank_advice_id = fields.Many2one('hr.bank.advice', string="Bank Advice")

# class EmployeeBankAcct(models.Model):
#     _name = 'hr.employee.bank.acct'
#
#     emp_id = fields.Many2one('hr.employee', string="Employee")
#     acct_no = fields.Many2one(string="Account Number", related='emp_id.bank_account_id', readonly=True)
#     bank_name = fields.Many2one(string="Bank Name", related='emp_id.bank_account_id.bank_id', readonly=True)
#     salary = fields.Integer(string="Salary")
#     bank_id = fields.Many2one('hr.bank.advice', string="Bank Name")