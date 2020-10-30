from openerp import models, fields, api, _
from IntuizApiMF import IntuizApiMF


class IntuizApiRiskMF(models.TransientModel):
    _name = "intuiz.api.risk.mf"
    _inherit = "intuiz.api.mf"

    @api.model
    def default_get(self, fields_list):
        res = super(IntuizApiRiskMF, self).default_get(fields_list=fields_list)
        res["uri_mf"] = "https://" + res["host_mf"] + "/iws-v3.18/services/CallistoRisqueSecure.CallistoRisqueSecureHttpsSoap11Endpoint/"
        return res

    def getPartnersTemp(self, siren):
        response = self.send(IntuizApiBodyIdentityGetPartnersMF(identification, siren))
        response_parsed = ET.fromstring(response)
        partners_temp_api = response_parsed[0][0][0].findall("{http://response.callisto.newsys.altares.fr/xsd}myInfo")
        partners_temp = []
        for partner_temp_api in partners_temp_api:
            partner_temp = self.env["res.partner.temp.mf"].create({
                "name": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}raisonSociale").text,
                "mf_score_mf": 21,
                "street_mf": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}rue").text,
                "city_mf": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}ville").text,
                "zip_mf": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}codePostal").text,
                "siret_mf": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}siret").text
            })
            partners_temp.append(partner_temp.id)
        return partners_temp