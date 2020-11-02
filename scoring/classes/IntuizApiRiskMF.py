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
        siren = partner.siret_number[0:9]
        response = self.send(IntuizApiBodyRiskGetScoreHistoryMF(self.user_mf, self.password_mf, siren))
        print("IntuizApiRiskMF.20")
        print(repr(partner));
        print("IntuizApiRiskMF.22")
        print(response)
        print("IntuizApiRiskMF.24")
        response_parsed = ET.fromstring(response)
        print("IntuizApiRiskMF.26")
        element_my_info = response_parsed[0][0][0].find("{http://response.callisto.newsys.altares.fr/xsd}myInfo")
        print("IntuizApiRiskMF.28")
        print(element_my_info)
        score_history_api = element_my_info.findall("{http://risque.vo.callisto.newsys.altares.fr/xsd}scoreList")
        print("IntuizApiRiskMF.31")
        print(score_history_api)

        score_history_temp = []
        for score_api in score_history_api:
            print("IntuizApiRiskMF.36")
            print(score_api)
            score_temp = self.env["score.mf"].create({
                "score_cent_mf": score_api.find("{http://risque.vo.callisto.newsys.altares.fr/xsd}scoreCent").text,
                "date_mf": score_api.find("{http://risque.vo.callisto.newsys.altares.fr/xsd}dateValeur").text,
                "partner_id": partner.id
            })
            score_history_temp.append(score_temp.id)
        return score_history_temp