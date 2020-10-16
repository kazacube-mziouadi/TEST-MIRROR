import requests
from openerp import models, fields, api, _
from IntuizApi import IntuizApi
from ResPartner import ResPartner
from IntuizMapInterface import IntuizMapInterface
import xml.etree.ElementTree as ET
from openerp.api import Environment as Env


class IntuizApiService():
    # Constructeur
    def __init__(self,
                 where,
                 who
                 ):
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

    def getPartners(self):
        response = self.send()
        response_parsed = ET.fromstring(response)
        partners_api = response_parsed[0][0][0].findall('{http://response.callisto.newsys.altares.fr/xsd}myInfo')
        partners = []
        for partner_api in partners_api:
            # TODO: arriver à créer un res_partner
            # partner = records.env['res.partner'].create()
            # partner.map_from_intuiz(partner_api)
            # partners.append(partner)
            print(partner_api)
        return partners
