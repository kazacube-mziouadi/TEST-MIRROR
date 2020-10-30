import hashlib
from openerp import models, fields, api, _
from ApiHeaderMF import ApiHeaderMF
import requests
import json


class IntuizApiMF(models.AbstractModel):
    _name = "intuiz.api.mf"
    _auto = False

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    host_mf = fields.Char(string='Host', size=128, required=False, help='')
    headers_mf = fields.Char(string='Headers', required=False, help='')
    uri_mf = fields.Char(string='Uri', required=False, help='')
    user_mf = fields.Char(string='User', required=False, help='')
    password_mf = fields.Char(string='Password', required=False, help='')

    @api.model
    def default_get(self, fields_list):
        res = super(IntuizApiMF, self).default_get(fields_list=fields_list)
        res["host_mf"] = "intuiz.altares.fr"  # host="https://intuiz.altares.fr/iws-v3.18/services/CallistoIdentiteObjectSecure.CallistoIdentiteObjectSecureHttpsSoap11Endpoint/",
        # res["user_mf"] = "U2019004798"
        # res["password_mf"] = self.set_password_sha1("1Life2020*")
        intuiz_api_mf = self.env["intuiz.api.credentials.mf"].search([], None, 1)
        res["user_mf"] = intuiz_api_mf.user_mf
        res["password_mf"] = intuiz_api_mf.password_mf
        api_header = ApiHeaderMF(res["host_mf"])
        res["headers_mf"] = api_header.get_formatted_headers()
        return res

    def send(self, intuiz_api_function_body):
        request = requests.post(self.uri_mf, headers=json.loads(self.headers_mf), data=intuiz_api_function_body.body)
        return request.content