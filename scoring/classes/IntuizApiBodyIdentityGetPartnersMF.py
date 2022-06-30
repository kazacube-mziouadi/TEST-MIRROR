from IntuizApiBodyInterfaceMF import IntuizApiBodyInterfaceMF


class IntuizApiBodyIdentityGetPartnersMF(IntuizApiBodyInterfaceMF):
    def __init__(self, user, password, where, who):
        self.body = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://serviceobject.service.callisto.newsys.altares.fr" xmlns:xsd="http://request.callisto.newsys.altares.fr/xsd">
   <soapenv:Header/>
   <soapenv:Body>
      <ser:doRechercheSimple>
         <!--Optional:-->
         <ser:request>
            <!--Optional:-->
            <xsd:identification>""" + user + """|""" + password + """</xsd:identification>
            <!--Optional:-->
            <xsd:refClient>recherche</xsd:refClient>
            <!--Optional:-->
            <xsd:categorieItemADeselectionner>1</xsd:categorieItemADeselectionner>
            <!--Optional:-->
            <xsd:categorieItemId></xsd:categorieItemId>
            <!--Optional:-->
            <xsd:contexteRecherche></xsd:contexteRecherche>
            <!--Optional:-->b
            <xsd:debutResultat>0</xsd:debutResultat>
            <!--Optional:-->
            <xsd:elargie>1</xsd:elargie>
            <!--Optional:-->
            <xsd:nbElt>200</xsd:nbElt>
            <!--Optional:-->
            <xsd:ou>""" + where + """</xsd:ou>
            <!--Optional:-->
            <xsd:qui>""" + who + """</xsd:qui>
            <!--Optional:-->
            <xsd:rechercheActif>0</xsd:rechercheActif>
            <!--Optional:-->
            <xsd:rechercheSiege>0</xsd:rechercheSiege>
         </ser:request>
      </ser:doRechercheSimple>
   </soapenv:Body>
</soapenv:Envelope>
        """