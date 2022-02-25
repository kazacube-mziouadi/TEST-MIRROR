# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import os
import base64


class WizardUploadFileMF(models.TransientModel):
    _name = "wizard.upload.file.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    file_name_mf = fields.Char("File to import name")
    file_to_import_mf = fields.Binary(string="File to import content", required=True)
    directory_mf = fields.Many2one("physical.directory.mf", string="Directory to upload file in")

    @api.model
    def default_get(self, fields_list):
        res = super(WizardUploadFileMF, self).default_get(fields_list=fields_list)
        res["directory_mf"] = self.env.context.get("directory_id")
        return res

    @api.multi
    def action_validate_upload(self):
        if not os.path.exists(self.directory_mf.path_mf):
            os.makedirs(self.directory_mf.path_mf)
        imported_file_decoded = str(base64.b64decode(self.file_to_import_mf))
        file_path = os.path.join(self.directory_mf.path_mf, self.file_name_mf)
        file = open(file_path, "a")
        file.write(imported_file_decoded)
        file.close()
        self.directory_mf.write({
            "files_mf": [(0, 0, {"name": self.file_name_mf})]
        })


