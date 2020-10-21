import hashlib
from openerp import models, fields, api, _
from ApiHeaderMF import ApiHeaderMF


class IntuizApiMF(models.AbstractModel):
    _name = "intuiz.api.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    host_mf = fields.Char(string='Host', size=64, required=False, help='')
    user_mf = fields.Char(string='User', size=64, required=False, help='')
    hash_password_mf = fields.Char(string='Hash Password', size=128, required=False, help='')
    headers_mf = fields.Char(string='Headers', size=128, required=False, help='')
    uri_mf = fields.Char(string='Uri', size=128, required=False, help='')

    @api.model
    def default_get(self, fields_list):
        res = super(IntuizApiMF, self).default_get(fields_list=fields_list)
        res["host_mf"] = "intuiz.altares.fr"  # host="https://intuiz.altares.fr/iws-v3.18/services/CallistoIdentiteObjectSecure.CallistoIdentiteObjectSecureHttpsSoap11Endpoint/",
        res["user_mf"] = "U2019004798"
        res["hash_password_mf"] = self.set_password_sha1("1Life2020*")
        res["headers_mf"] = ApiHeaderMF(res["host_mf"])
        return res

    def set_password_sha1(self, clear_password):
        hash_lib_sha1 = hashlib.sha1()
        # TODO: Breaking change : bytes() non fonctionnel a partir de Python 3.0.0 => bytes(str, "utf8")
        hash_lib_sha1.update(bytes(clear_password))
        return hash_lib_sha1.hexdigest()




