from openerp import models, fields, api, _

class wizard_refresh_from_intuiz(models.TransientModel):
    _name = 'wizard.partner.refresh.intuiz'

    @api.model
    def default_get(self, fields_list):
        res = super(wizard_refresh_from_intuiz, self).default_get(fields_list=fields_list)
        res['partner_ids'] = self.env.context.get('active_ids')
        return res

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string='Name', size=32, required=False)
    partner_ids = fields.Many2many('res.partner', 'wizard_partner_refresh_from_intuiz_res_partner_rel', 'wiz_refresh_id', 'partner_id',
                                   string='Partner', copy=False)
