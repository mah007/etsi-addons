from odoo import api, models, fields

class Institution(models.Model):
    _inherit = 'res.partner'

    # Institution: True
    @api.model
    def default_get(self, fields):
        context = self.env.context
        result = super(Institution, self).default_get(fields)
        # print 'context', context
        if context:
            if 'institution' in context:
                if context['institution']:
                    result['is_institution'] = True
                    result['is_company'] = True
        return result

    is_institution = fields.Boolean(string="Institution")



