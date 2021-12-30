# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import os
import base64
from openerp.addons.myfab_file_interface.classes.files.PhysicalFileMF import PhysicalFileMF


class WizardUploadImportFileMF(models.TransientModel):
    _name = "wizard.upload.import.file.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    file_name_mf = fields.Char("File to import name")
    file_to_import_mf = fields.Binary(string="File to import content", required=True)
    file_interface_import_mf = fields.Many2one("file.interface.import.mf", string="File Interface Import to launch")

    @api.model
    def default_get(self, fields_list):
        res = super(WizardUploadImportFileMF, self).default_get(fields_list=fields_list)
        res["file_interface_import_mf"] = self.env.context.get("file_interface_import_id")
        return res

    @api.multi
    def action_validate_upload(self):
        if not os.path.exists(self.file_interface_import_mf.import_directory_path_mf):
            os.makedirs(self.file_interface_import_mf.import_directory_path_mf)
        imported_file_decoded = str(base64.b64decode(self.file_to_import_mf))
        file_path = os.path.join(self.file_interface_import_mf.import_directory_path_mf, self.file_name_mf)
        file = open(file_path, "a")
        file.write(imported_file_decoded)
        file.close()
        self.file_interface_import_mf.write({
            "files_to_import_mf": [(0, 0, {
                "name": self.file_name_mf,
                "directory_path_mf": self.file_interface_import_mf.import_directory_path_mf,
                "content_mf": self.file_to_import_mf,
                "last_modification_date_mf": PhysicalFileMF.get_last_modification_date(
                    self.file_interface_import_mf.import_directory_path_mf,
                    self.file_name_mf
                )
            })]
        })


