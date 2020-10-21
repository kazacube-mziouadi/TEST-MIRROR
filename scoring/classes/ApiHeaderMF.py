import hashlib
from openerp import models, fields, api, _


class ApiHeaderMF:
    # Constructeur
    def __init__(self,
                 host,
                 accept="*/*",
                 accept_encoding="gzip, deflate, br",
                 connection="keep-alive",
                 content_type="text/xml",
                 accept_charset="UTF-8"
                 ):
        self.host = host
        self.accept = accept
        self.accept_encoding = accept_encoding
        self.connection = connection
        self.content_type = content_type
        self.accept_charset = accept_charset

    def get_formatted_header(self):
        return {
            "Host": self.host,
            "Accept": self.accept,
            "Accept-Encoding": self.accept_encoding,
            "Connection": self.connection,
            "Content-Type": self.content_type,
            "Accept-Charset": self.accept_charset,
        }


