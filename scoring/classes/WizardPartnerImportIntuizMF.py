from openerp import models, fields, api, _
import xml.etree.ElementTree as ET


class WizardPartnerImportIntuizMF(models.TransientModel):
    _name = "wizard.partner.import.intuiz.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    res_partner_temp_ids = fields.Many2many('res.partner.temp.mf', 'wizard_partner_import_intuiz_mf_res_partner_temp_mf_rel',
                                            'wiz_import_id', 'partner_temp_id', string='Partner', copy=False)

    @api.model
    def default_get(self, fields_list):
        res = super(WizardPartnerImportIntuizMF, self).default_get(fields_list=fields_list)
        print('GOING THERE')
        intuiz_api_identity = self.env["intuiz.api.identity.mf"].create({})
        res_partner_temp_ids = intuiz_api_identity.getPartnersTemp("69", "1LIFE")
        res["res_partner_temp_ids"] = res_partner_temp_ids
        return res

    @api.multi
    def action_validate(self):
        print("VALIDATE ACTION")
