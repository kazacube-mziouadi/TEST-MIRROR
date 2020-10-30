import hashlib
from openerp import models, fields, api, _
from ApiHeaderMF import ApiHeaderMF
import requests
import json

class IntuizApiCredentialsMF(models.Model):
    _name = "intuiz.api.credentials.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    user_mf = fields.Char(string='User', size=128, required=False, help='')
    password = fields.Char(string='Password', required=False, help='', store=True)
    hash_password_mf = fields.Char(compute='_encrypt_password', store=True)

    @api.one
    @api.depends('password')
    def _encrypt_password(self):
        self.hash_password_mf = self.set_password_sha1(self.password)
        self.password = ""

    def set_password_sha1(self, clear_password):
        return hashlib.sha1(clear_password).hexdigest()
