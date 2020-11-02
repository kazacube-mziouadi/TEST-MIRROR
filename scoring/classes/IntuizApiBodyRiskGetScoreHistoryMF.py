from IntuizApiBodyInterfaceMF import IntuizApiBodyInterfaceMF


class IntuizApiBodyRiskGetScoreHistoryMF(IntuizApiBodyInterfaceMF):
    def __init__(self, user, password, siren):
        print("IntuizApiBodyRiskGetScoreHistoryMF.6")
        print(siren)
        self.body = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.callisto.newsys.altares.fr">
   <soapenv:Header/>
   <soapenv:Body>
      <ser:getHistoriqueScore>
         <!--Optional:-->
         <ser:identification>""" + user + "|" + password + """</ser:identification>
         <!--Optional:-->
         <ser:refClient>?</ser:refClient>
         <!--Optional:-->
         <ser:siren>""" + siren + """</ser:siren>
      </ser:getHistoriqueScore>
   </soapenv:Body>
</soapenv:Envelope>
        """
