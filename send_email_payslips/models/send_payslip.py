# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2015-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Nilmar Shereef(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# from openerp import models, api
from odoo import api, fields, models

class SendPayslips(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread']

    @api.multi
    def send_payslip(self):
        """
        This function opens a window to compose an email, with the edi payslip template message loaded by default
        """
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('send_email_payslips', 'email_template_hr_payslip')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        print 'user', self.employee_id.user_id

        user = self.env['res.users'].browse(self.employee_id.user_id.id)
        print 'partner_id', user.partner_id.id
        ctx = dict()
        ctx.update({
            'default_model': 'hr.payslip',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_partner_id': user.partner_id.id,
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

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):
        """ Handle composition mode. Some details about context keys:
            - comment: default mode, model and ID of a record the user comments
                - default_model or active_model
                - default_res_id or active_id
            - reply: active_id of a message the user replies to
                - default_parent_id or message_id or active_id: ID of the
                    mail.message we reply to
                - message.res_model or default_model
                - message.res_id or default_res_id
            - mass_mail: model and IDs of records the user mass-mails
                - active_ids: record IDs
                - default_model or active_model
        """
        result = super(MailComposer, self).default_get(fields)

        # v6.1 compatibility mode
        print 'context', self._context.get('default_partner_id')
        result['composition_mode'] = result.get('composition_mode',
                                                self._context.get('mail.compose.message.mode', 'comment'))
        result['model'] = result.get('model', self._context.get('active_model'))
        result['res_id'] = result.get('res_id', self._context.get('active_id'))
        result['parent_id'] = result.get('parent_id', self._context.get('message_id'))
        #add this line of code below to get the default partner
        result['partner_ids'] = [(self._context.get('default_partner_id'))]
        if 'no_auto_thread' not in result and (
                result['model'] not in self.env or not hasattr(self.env[result['model']], 'message_post')):
            result['no_auto_thread'] = True

        # default values according to composition mode - NOTE: reply is deprecated, fall back on comment
        if result['composition_mode'] == 'reply':
            result['composition_mode'] = 'comment'
        vals = {}
        if 'active_domain' in self._context:  # not context.get() because we want to keep global [] domains
            vals['use_active_domain'] = True
            vals['active_domain'] = '%s' % self._context.get('active_domain')
        if result['composition_mode'] == 'comment':
            vals.update(self.get_record_data(result))

        for field in vals:
            if field in fields:
                result[field] = vals[field]

        # TDE HACK: as mailboxes used default_model='res.users' and default_res_id=uid
        # (because of lack of an accessible pid), creating a message on its own
        # profile may crash (res_users does not allow writing on it)
        # Posting on its own profile works (res_users redirect to res_partner)
        # but when creating the mail.message to create the mail.compose.message
        # access rights issues may rise
        # We therefore directly change the model and res_id
        if result['model'] == 'res.users' and result['res_id'] == self._uid:
            result['model'] = 'res.partner'
            result['res_id'] = self.env.user.partner_id.id

        if fields is not None:
            [result.pop(field, None) for field in result.keys() if field not in fields]
        return result
