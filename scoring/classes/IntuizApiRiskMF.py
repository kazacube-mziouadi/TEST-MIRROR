from openerp import models, fields, api, _
from IntuizApiMF import IntuizApiMF


class IntuizApiRiskMF(models.TransientModel):
    _name = "intuiz.api.risk.mf"
    _inherit = "intuiz.api.mf"

    @api.model
    def default_get(self, fields_list):
        res = super(IntuizApiRiskMF, self).default_get(fields_list=fields_list)
        # TODO : instantiate Risk uri
        res["uri_mf"] = "https://" + res["host_mf"] + "/iws-v3.18/services/CallistoIdentiteObjectSecure.CallistoIdentiteObjectSecureHttpsSoap11Endpoint/"
        return res
