from odoo import models, fields, api


class ReportJobOffer(models.AbstractModel):
    _name = 'report.etsi_hrms.job_offer_template'



    @api.multi
    def render_html(self, docids, data={}):
        print 'yes'
        data = data if data is not None else {}
        docs = self.env['hr.applicant'].browse(docids)
        for rec in docs:
            advantages_id = rec.advantages_id.id
            res_jo_signature = self.env['job_offer.signatures'].search([('advantages_id','=',advantages_id)])
            signatures = {}
            for rec_jo_signature in res_jo_signature:
                name = rec_jo_signature.name
                self.env.cr.execute('SELECT employee_id from jo_signature_emp_rel where jo_signature_id = %s' % rec_jo_signature.id)
                res = self.env.cr.fetchall()
                emp_ids = []
                for rec in res:
                    emp_id = rec[0]
                    emp_obj = self.env['hr.employee'].browse(emp_id)
                    emp_ids.append(emp_obj)
                signatures.update({name: emp_ids})
            data.update({'signatures':signatures})


        docargs = {
            'doc_ids': docids,
            'doc_model': 'hr.applicant',
            'docs': docs,
            'data': data,
        }


        return self.env['report'].render('etsi_hrms.job_offer_template',docargs)


