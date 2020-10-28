from openerp import models, fields, api, _
import xml.etree.ElementTree as ET


class WizardPartnerImportIntuizResultMF(models.TransientModel):
    _name = "wizard.partner.import.intuiz.result.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    where_mf = fields.Char(string="Where", size=128, required=False)
    who_mf = fields.Char(string="Who", size=128, required=False)
    res_partner_temp_ids = fields.Many2many('res.partner.temp.mf', 'wizard_partner_import_intuiz_mf_res_partner_temp_mf_rel',
                                            'wiz_import_id', 'partner_temp_id', string='Partner', copy=False)

    @api.model
    def default_get(self, fields_list):
        res = super(WizardPartnerImportIntuizResultMF, self).default_get(fields_list=fields_list)
        intuiz_api_identity = self.env["intuiz.api.identity.mf"].create({})
        res_partner_temp_ids = intuiz_api_identity.getPartnersTemp(self.env.context.get('where'), self.env.context.get('who'))
        res["res_partner_temp_ids"] = res_partner_temp_ids
        return res

    @api.multi
    def action_validate(self):
        print("VALIDATE ACTION")
