from openerp import models, fields, api, _
from ResPartner import ResPartner


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
        for partner_selected_id in self.env.context.get("active_ids"):
            partner_selected = self.env["res.partner"].search([["id", "=", partner_selected_id]], None, 1)
            res_partner_temps = intuiz_api_identity.get_partners_temp(partner_selected.zip,
                                                                    partner_selected.siret_number)
            res_partner_temp = self.env["res.partner.temp.mf"].search([["id", "=", res_partner_temps[0]]], None, 1)
            partner_selected.write(ResPartner.create_from_object_temp(self, res_partner_temp, False))
            for score in partner_selected.score_history_mf:
                score.unlink()
            intuiz_api_risk = self.env["intuiz.api.risk.mf"].create({})
            intuiz_api_risk.get_score_history(partner_selected)
        return res
