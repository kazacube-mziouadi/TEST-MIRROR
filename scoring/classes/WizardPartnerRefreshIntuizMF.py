from openerp import models, fields, api, _


class WizardPartnerRefreshIntuizMF(models.TransientModel):
    _name = "wizard.partner.refresh.intuiz.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)

    @api.model
    def default_get(self, fields_list):
        res = super(WizardPartnerRefreshIntuizMF, self).default_get(fields_list=fields_list)
        intuiz_api_identity = self.env["intuiz.api.identity.mf"].create({})
        print(self.env.context.get("active_ids"))
        for partner_selected_id in self.env.context.get("active_ids"):
            partner_selected = self.env["res.partner"].search([["id", "=", partner_selected_id]], None, 1)
            print(partner_selected)
            res_partner_temps = intuiz_api_identity.getPartnersTemp(partner_selected.zip,
                                                                    partner_selected.siret_number)
            res_partner_temp = self.env["res.partner.temp.mf"].search([["id", "=", res_partner_temps[0]]], None, 1)
            print(res_partner_temp)
            partner_selected.write({
                "name": res_partner_temp.name,
                "score_mf": res_partner_temp.score_mf,
                "street": res_partner_temp.street_mf,
                "city": res_partner_temp.city_mf,
                "zip": res_partner_temp.zip_mf,
                "reference": res_partner_temp.siret_mf
            })
        return res
