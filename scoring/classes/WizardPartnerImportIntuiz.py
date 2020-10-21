from openerp import models, fields, api, _
import xml.etree.ElementTree as ET
from IntuizApiService import IntuizApiService


class WizardPartnerImportIntuiz(models.TransientModel):
    _name = "wizard.partner.import.intuiz"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    res_partner_temp_ids = fields.Many2many('res.partner.temp', 'wizard_partner_import_intuiz_res_partner_temp_rel',
                                            'wiz_import_id', 'partner_temp_id', string='Partner', copy=False)

    @api.model
    def default_get(self, fields_list):
        res = super(WizardPartnerImportIntuiz, self).default_get(fields_list=fields_list)
        intuiz_api_service = IntuizApiService(self.env, "", "")
        res_partner_temp_ids = intuiz_api_service.getPartnersTemp()
        res["res_partner_temp_ids"] = res_partner_temp_ids
        return res

    @api.multi
    def action_validate(self):
        print("VALIDATE ACTION")
        # intuiz_api_service = IntuizApiService(self.id, self.env, "", "")
        # res_partner_temp_ids = intuiz_api_service.getPartnersTemp()
