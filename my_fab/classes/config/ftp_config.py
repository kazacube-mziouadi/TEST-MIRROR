# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_ftp_config(models.Model):
    _name = 'mf.ftp.config'
    _sql_constraints = [
        (
            "mf_ftp_config_uniq_adress",
            "UNIQUE(mf_type)",
            "There can only be one ftp config per type"
        )
    ]

    mf_ftp_adress = fields.Char(string="FTP adress")
    mf_login = fields.Char(string="Login")
    mf_password = fields.Char(string="Password")
    mf_folder_path = fields.Char(string="Folder Path")
    mf_type = fields.Selection('_mf_get_ftp_type',string="FTP type")

    @api.model
    def _mf_method_to_apply_get(self):
        return []