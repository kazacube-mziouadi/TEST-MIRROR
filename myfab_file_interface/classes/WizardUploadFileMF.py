# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import os
import datetime
import base64


class WizardUploadImportFileMF(models.TransientModel):
    _name = 'wizard.upload.import.file.mf'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    file_to_import_mf = fields.Binary(string='File to import', required=True, ondelete='restrict')
    upload_directory_mf = fields.Char(string="Upload directory")

    @api.model
    def default_get(self, fields_list):
        res = super(WizardUploadImportFileMF, self).default_get(fields_list=fields_list)
        res["upload_directory_mf"] = self.env.context.get("upload_directory_mf")
        return res

    @api.multi
    def action_validate_upload(self):
        json_file_decoded = str(base64.b64decode(self.file_to_import_mf))
        now = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y%m%d_%H%M%S")
        file_name = self.env.user.name + "-Import-WorkOrders-" + now + ".json"
        file_path = os.path.join(self.upload_directory_mf, file_name)
        file = open(file_path, "a")
        file.write(json_file_decoded)
        file.close()

