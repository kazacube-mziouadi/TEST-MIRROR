from openerp import models, fields, api, _


class WizardPartnerRefreshIntuizMF(models.TransientModel):
    _name = 'wizard.partner.refresh.intuiz.mf'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string='Name', size=32, required=False)
    partner_ids = fields.Many2many('res.partner', 'wizard_partner_refresh_intuiz_mf_res_partner_temp_mf_rel',
                                   'wiz_refresh_id', 'res_partner_temp_id', string='Partner', copy=False)

    @api.model
    def default_get(self, fields_list):
        res = super(WizardPartnerRefreshIntuizMF, self).default_get(fields_list=fields_list)
        res['partner_ids'] = self.env.context.get('active_ids')
        return res
