# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import os
import base64


class WizardUploadImportFileMF(models.TransientModel):
    _name = "wizard.upload.import.file.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    file_name = fields.Char("File to import name")
    file_to_import_mf = fields.Binary(string="File to import content", required=True, ondelete="restrict")
    upload_directory_mf = fields.Char(string="Upload directory")

    @api.model
    def default_get(self, fields_list):
        res = super(WizardUploadImportFileMF, self).default_get(fields_list=fields_list)
        res["upload_directory_mf"] = self.env.context.get("upload_directory_mf")
        return res

    @api.multi
    def action_validate_upload(self):
        if not os.path.exists(self.upload_directory_mf):
            os.makedirs(self.upload_directory_mf)
        imported_file_decoded = str(base64.b64decode(self.file_to_import_mf))
        file_path = os.path.join(self.upload_directory_mf, self.file_name)
        file = open(file_path, "a")
        file.write(imported_file_decoded)
        file.close()

