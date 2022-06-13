from openerp import models, fields, api, _
from ResPartner import ResPartner


class WizardPartnerRefreshIntuizScoreMF(models.TransientModel):
    _name = "wizard.partner.refresh.intuiz.score.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)

    @api.model
    def default_get(self, fields_list):
        res = super(WizardPartnerRefreshIntuizScoreMF, self).default_get(fields_list=fields_list)
        intuiz_api_risk = self.env["intuiz.api.risk.mf"].create({})
        for partner_selected_id in self.env.context.get("active_ids"):
            partner_selected = self.env["res.partner"].search([["id", "=", partner_selected_id]], None, 1)
            for score in partner_selected.score_history_mf:
                score.unlink()
            intuiz_api_risk.get_score_history(partner_selected)
        return res
