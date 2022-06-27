from openerp import models, fields, api, _
import xml.etree.ElementTree as ET


class WizardPartnerImportIntuizSearchMF(models.TransientModel):
    _name = "wizard.partner.import.intuiz.search.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    where_mf = fields.Char(string="Where", size=128, required=False)
    who_mf = fields.Char(string="Who", size=128, required=False)

    @api.multi
    def button_return_wizard_search_result(self):
        return {
            'name': _("Import from Intuiz Result"),
            'view_mode': 'form',
            'res_model': 'wizard.partner.import.intuiz.result.mf',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'where': self.where_mf, 'who': self.who_mf}
        }
