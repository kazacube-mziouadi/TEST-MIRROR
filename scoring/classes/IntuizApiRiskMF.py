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
        print("IntuizApiRiskMF.19")
        print(response)
        print("IntuizApiRiskMF.22")
        response_parsed = ET.fromstring(response)
        print("IntuizApiRiskMF.24")
        # sub_keys = response_parsed.text
        # for subKey in sub_keys:
        # print(sub_keys)

        # THIS METHOD DIDN'T WORK (prefixe soapenv not found in prefix map)
        # print("IntuizApiRiskMF.30")
        # element_my_info = response_parsed.find("soapenv:Envelope")
        # print(element_my_info)
        # print(element_my_info.text)

        # THIS METHOD DIDN'T WORK (prefixe soapenv not found in prefix map)
        # print("IntuizApiRiskMF.36")
        # element_my_info = response_parsed.find("soapenv:Body")
        # print(element_my_info)
        # print(element_my_info.text)

        # THIS METHOD DIDN'T WORK (prefixe ax297 not found in prefix map)
        # print("IntuizApiRiskMF.42")
        # element_my_info = response_parsed.find("ax297:myInfo")
        # print(element_my_info)
        # print(element_my_info.text)

        # THIS METHOD DIDN'T WORK (prefixe ax297 not found in prefix map)
        # print("IntuizApiRiskMF.48")
        # element_my_info = response_parsed[0].find("ax297:myInfo")
        # print(element_my_info)
        # print(element_my_info.text)

        # THIS METHOD DIDN'T WORK (prefixe ax297 not found in prefix map)
        # print("IntuizApiRiskMF.54")
        # element_my_info = response_parsed[0][0].find("ax297:myInfo")
        # print(element_my_info)
        # print(element_my_info.text)


        print("IntuizApiRiskMF.60")
        element_my_info = response_parsed[0][0][0].find("ax297:myInfo")
        print(element_my_info)
        print(element_my_info.text)


        print("IntuizApiRiskMF.66")
        element_my_info = response_parsed[0][0][0][0].find("ax297:myInfo")
        print(element_my_info)
        print(element_my_info.text)
        # THIS METHOD DIDN'T WORK (no findAll on element)
        # element_my_info = response_parsed[0][0][0].find("{http://response.callisto.newsys.altares.fr/xsd}myInfo")
        # score_history_api = element_my_info.findAll("{http://response.callisto.newsys.altares.fr/xsd}scoreList")
        # print("IntuizApiRiskMF.27")
        # print(score_history_api)

        # THIS METHOD DIDN'T WORK (return none)
        # score_history_api = response_parsed[0][0][0][3].find("{http://response.callisto.newsys.altares.fr/xsd}scoreList")
        # print("IntuizApiRiskMF.32")
        # print(score_history_api)

        # THIS METHOD DIDN'T WORK (return none)
        # score_history_api = response_parsed[0][0][0].find("{http://response.callisto.newsys.altares.fr/xsd}scoreList")
        # print("IntuizApiRiskMF.37")
        # print(score_history_api)

        # THIS METHOD DIDN'T WORK (no findAll on element)
        score_history_api = response_parsed[0][0][0].find("{http://response.callisto.newsys.altares.fr/xsd}myInfo").findAll("{http://response.callisto.newsys.altares.fr/xsd}scoreList")
        print("IntuizApiRiskMF.50")
        print(score_history_api)

        score_history_temp = []
        for score_api in score_history_api:
            print("IntuizApiRiskMF.55")
            print(score_api)
            score_temp = self.env["res.partner.temp.mf"].create({
                "score_cent_mf": score_api.find("{http://vo.callisto.newsys.altares.fr/xsd}scoreCent").text,
                "date_mf": score_api.find("{http://vo.callisto.newsys.altares.fr/xsd}dateValeur").text,
                "partner_id": partner.id
            })
            score_history_temp.append(score_temp.id)
        return score_history_temp