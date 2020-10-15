import requests
from openerp import models, fields, api, _

class IntuizApiSearch():
    # Constructeur
    def __init__(self,
                 intuiz_api,
                 where,
                 who
                 ):
        self.where = where
        self.who = who
        self.intuiz_api = intuiz_api
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
        return request, request.content