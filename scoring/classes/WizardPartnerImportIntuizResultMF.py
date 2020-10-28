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
    res_partner_temps = fields.Many2many('res.partner.temp.mf', 'wizard_partner_import_intuiz_mf_res_partner_temps_mf_rel',
                                            'wiz_import_id', 'partner_temp_id', string='Partner', copy=False, readonly=False)

    @api.model
    def default_get(self, fields_list):
        res = super(WizardPartnerImportIntuizResultMF, self).default_get(fields_list=fields_list)
        intuiz_api_identity = self.env["intuiz.api.identity.mf"].create({})
        res_partner_temps = intuiz_api_identity.getPartnersTemp(self.env.context.get('where'), self.env.context.get('who'))
        res["res_partner_temps"] = res_partner_temps
        return res

    @api.multi
    def action_validate(self):
        print("VALIDATE ACTION")
        for partner_temp in self.res_partner_temps:
            if partner_temp.selected:
                # TODO : create res_partner fr
                print("")

