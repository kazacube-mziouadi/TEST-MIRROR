from IntuizApiBodyInterfaceMF import IntuizApiBodyInterfaceMF


class IntuizApiBodyRiskGetScoreHistoryMF(IntuizApiBodyInterfaceMF):
    def __init__(self, identification, siren):
        self.body = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.callisto.newsys.altares.fr">
   <soapenv:Header/>
   <soapenv:Body>
      <ser:getHistoriqueScore>
         <!--Optional:-->
         <ser:identification>""" + identification + """</ser:identification>
         <!--Optional:-->
         <ser:refClient>?</ser:refClient>
         <!--Optional:-->
         <ser:siren>""" + siren + """</ser:siren>
      </ser:getHistoriqueScore>
   </soapenv:Body>
</soapenv:Envelope>
        """
