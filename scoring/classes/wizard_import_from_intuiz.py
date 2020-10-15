from openerp import models, fields, api, _

class wizard_import_from_intuiz(models.TransientModel):
    _name = 'wizard.partner.import.intuiz'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string='Name', size=32, required=False)
    partner_ids = fields.Many2many('res.partner', 'wizard_partner_import_from_intuiz_res_partner_rel', 'wiz_import_id', 'partner_id',
                                   string='Partner', copy=False)