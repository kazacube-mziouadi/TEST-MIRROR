from openerp import models, fields, api, _
import xml.etree.ElementTree as ET
from IntuizApiBodyRiskGetScoreHistoryMF import IntuizApiBodyRiskGetScoreHistoryMF
from IntuizApiMF import IntuizApiMF


class IntuizApiRiskMF(models.TransientModel):
    _name = "intuiz.api.risk.mf"
    _inherit = "intuiz.api.mf"

    @api.model
    def default_get(self, fields_list):
        res = super(IntuizApiRiskMF, self).default_get(fields_list=fields_list)
        res["uri_mf"] = "https://" + res["host_mf"] + "/iws-v3.18/services/CallistoRisqueSecure.CallistoRisqueSecureHttpsSoap11Endpoint/"
        return res

    def get_score_history(self, partner):
        response = self.send(IntuizApiBodyRiskGetScoreHistoryMF(self.user_mf, self.password_mf, partner.siret_number))
        response_parsed = ET.fromstring(response)
        score_history_api = response_parsed[0][0][0].find("{http://response.callisto.newsys.altares.fr/xsd}myInfo").findAll("{http://response.callisto.newsys.altares.fr/xsd}scoreList")
        print(score_history_api)
        score_history_temp = []
        for score_api in score_history_api:
            print(score_api)
            score_temp = self.env["res.partner.temp.mf"].create({
                "score_cent_mf": score_api.find("{http://vo.callisto.newsys.altares.fr/xsd}scoreCent").text,
                "date_mf": score_api.find("{http://vo.callisto.newsys.altares.fr/xsd}dateValeur").text,
                "partner_id": partner.id
            })
            score_history_temp.append(score_temp.id)
        return score_history_temp