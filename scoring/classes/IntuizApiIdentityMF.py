from openerp import models, fields, api, _
from IntuizApiMF import IntuizApiMF


class IntuizApiIdentityMF(models.Model):
    _name = "intuiz.api.identity.mf"
    _inherit = "intuiz.api.mf"

    @api.model
    def default_get(self, fields_list):
        res = super(IntuizApiIdentityMF, self).default_get(fields_list=fields_list)
        # TODO : instantiate Identity uri
        res["uri_mf"] = "https://" + res["host_mf"] + "/iws-v3.18/services/CallistoIdentiteObjectSecure.CallistoIdentiteObjectSecureHttpsSoap11Endpoint/"
        return res
