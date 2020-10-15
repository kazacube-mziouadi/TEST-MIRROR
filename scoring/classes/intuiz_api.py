import hashlib
from openerp import models, fields, api, _

class IntuizApi(object):
    # Constructeur
    def __init__(self,
                 host = "intuiz.altares.fr",  #host="https://intuiz.altares.fr/iws-v3.18/services/CallistoIdentiteObjectSecure.CallistoIdentiteObjectSecureHttpsSoap11Endpoint/",
                 user = "U2019004798",
                 pwd = "1Life2020*", # SHA-1 : 6c0dcf59bb30429d8ed449048e3ef6fe689cff9a
                 ):
        self.host = host
        self.user = user
        self.pwd  = pwd
        self.hash_pwd = hashlib.sha1()
        self.hash_pwd.update(pwd)
        self.headers = {
            "Host": self.host,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Content-Type": "text/xml",
            "Accept-Charset": "UTF-8",
        }
        self.uri = u"https://{host}'/iws-v3.18/services/CallistoIdentiteObjectSecure.CallistoIdentiteObjectSecureHttpsSoap11Endpoint/'".format(host=self.host)




