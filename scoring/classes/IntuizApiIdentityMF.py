from openerp import models, fields, api, _
import xml.etree.ElementTree as ET
from IntuizApiBodyIdentityGetPartnersMF import IntuizApiBodyIdentityGetPartnersMF
from ResPartnerTempMF import ResPartnerTempMF
from IntuizApiMF import IntuizApiMF


class IntuizApiIdentityMF(models.TransientModel):
    _name = "intuiz.api.identity.mf"
    _inherit = "intuiz.api.mf"

    @api.model
    def default_get(self, fields_list):
        res = super(IntuizApiIdentityMF, self).default_get(fields_list=fields_list)
        # TODO : instantiate Identity uri
        res["uri_mf"] = "https://" + res["host_mf"] + "/iws-v3.18/services/CallistoIdentiteObjectSecure.CallistoIdentiteObjectSecureHttpsSoap11Endpoint/"
        return res

    def get_partners_temp(self, where, who):
        response = self.send(IntuizApiBodyIdentityGetPartnersMF(self.user_mf, self.password_mf, where, who))
        response_parsed = ET.fromstring(response)
        partners_temp_api = response_parsed[0][0][0].findall("{http://response.callisto.newsys.altares.fr/xsd}myInfo")
        partners_temp = []
        for partner_temp_api in partners_temp_api:
            partner_temp = self.env["res.partner.temp.mf"].create(ResPartnerTempMF.create_from_object_temp(partner_temp_api))
            partners_temp.append(partner_temp.id)
        return partners_temp