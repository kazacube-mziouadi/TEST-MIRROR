import requests
from openerp import models, fields, api, _
from IntuizApi import IntuizApi
import xml.etree.ElementTree as ET


class IntuizApiService():

    # Constructeur
    def __init__(
            self,
            env,
            where,
            who
            ):
        self.env = env
        self.where = where
        self.who = who
        self.intuiz_api = IntuizApi()
        self.body = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://serviceobject.service.callisto.newsys.altares.fr" xmlns:xsd="http://request.callisto.newsys.altares.fr/xsd">
   <soapenv:Header/>
   <soapenv:Body>
      <ser:doRechercheSimple>
         <!--Optional:-->
         <ser:request>
            <!--Optional:-->
            <xsd:identification>U2019004798|6c0dcf59bb30429d8ed449048e3ef6fe689cff9a</xsd:identification>
            <!--Optional:-->
            <xsd:refClient>recherche</xsd:refClient>
            <!--Optional:-->
            <xsd:categorieItemADeselectionner>1</xsd:categorieItemADeselectionner>
            <!--Optional:-->
            <xsd:categorieItemId></xsd:categorieItemId>
            <!--Optional:-->
            <xsd:contexteRecherche></xsd:contexteRecherche>
            <!--Optional:-->
            <xsd:debutResultat>0</xsd:debutResultat>
            <!--Optional:-->
            <xsd:elargie>1</xsd:elargie>
            <!--Optional:-->
            <xsd:nbElt>200</xsd:nbElt>
            <!--Optional:-->
            <xsd:ou>69</xsd:ou>
            <!--Optional:-->
            <xsd:qui>1Life</xsd:qui>
            <!--Optional:-->
            <xsd:rechercheActif>0</xsd:rechercheActif>
            <!--Optional:-->
            <xsd:rechercheSiege>0</xsd:rechercheSiege>
         </ser:request>
      </ser:doRechercheSimple>
   </soapenv:Body>
</soapenv:Envelope>
        """

    def send(self):
        request = requests.post(self.intuiz_api.uri, headers=self.intuiz_api.headers, data=self.body)
        return request.content

    def getPartnersTemp(self):
        response = self.send()
        response_parsed = ET.fromstring(response)
        partners_temp_api = response_parsed[0][0][0].findall('{http://response.callisto.newsys.altares.fr/xsd}myInfo')
        partners_temp = []
        for partner_temp_api in partners_temp_api:
            # print(partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}raisonSociale").text)
            # for partner_temp_api_attr in partner_temp_api:
            #     print(partner_temp_api_attr)
            partner_temp = self.env["res.partner.temp"].create({
                "name": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}raisonSociale").text,
                "mf_score": 21,
                "street": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}rue").text,
                "city": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}ville").text,
                "zip": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}codePostal").text,
                "website": "",
                "siret": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}siret").text
            })
            partners_temp.append(partner_temp.id)
        # wizard = self.env["wizard.partner.import.intuiz"].search([("id", '=', self.wizard.id)])
        # print(wizard.res_partner_temp_ids)
        return partners_temp
