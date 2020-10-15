from openerp import models, fields, api, _

class WizardRefreshFromIntuiz(models.TransientModel):
    _name = 'wizard.partner.refresh.intuiz'

    @api.model
    def default_get(self, fields_list):
        res = super(WizardRefreshFromIntuiz, self).default_get(fields_list=fields_list)
        res['partner_ids'] = self.env.context.get('active_ids')
        return res

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string='Name', size=32, required=False)
    partner_ids = fields.Many2many('res.partner', 'wizard_partner_refresh_from_intuiz_res_partner_rel', 'wiz_refresh_id', 'partner_id',
                                   string='Partner', copy=False)
