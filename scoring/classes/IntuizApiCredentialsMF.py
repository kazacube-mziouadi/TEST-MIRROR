import hashlib
from openerp import models, fields, api, _


class IntuizApiCredentialsMF(models.Model):
    _name = "intuiz.api.credentials.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    user_mf = fields.Char(string='User', size=128, required=False, help='')
    password_mf = fields.Char(string='Password', required=False, help='', store=False)
    hash_password_mf = fields.Char(compute='_encrypt_password', store=True)

    @api.model
    def create(self, fields_list):
        fields_list["hash_password_mf"] = self.set_password_sha1(fields_list["password_mf"])
        return super(IntuizApiCredentialsMF, self).create(fields_list)

    def set_password_sha1(self, clear_password):
        return hashlib.sha1(clear_password).hexdigest()
