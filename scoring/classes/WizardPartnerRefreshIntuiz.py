from openerp import models, fields, api, _


class WizardPartnerRefreshIntuiz(models.TransientModel):
    _name = 'wizard.partner.refresh.intuiz'

    @api.model
    def default_get(self, fields_list):
        res = super(WizardPartnerRefreshIntuiz, self).default_get(fields_list=fields_list)
        res['partner_ids'] = self.env.context.get('active_ids')
        return res

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string='Name', size=32, required=False)
    partner_ids = fields.Many2many('res.partner', 'wizard_partner_refresh_intuiz_res_partner_temp_rel',
                                   'wiz_refresh_id', 'res_partner_temp_id', string='Partner', copy=False)
