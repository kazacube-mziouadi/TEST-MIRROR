from openerp import models, fields, api, registry, _
import os
from datetime import datetime
import base64


class PhysicalFileMF(models.TransientModel):
    _inherit = "file.mf"
    _name = "physical.file.mf"
    _description = "MyFab physical file"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    last_modification_date_mf = fields.Datetime(string="Last modification date")
    directory_mf = fields.Many2one("physical.directory.mf", string="Directory")

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.model
    def create(self, fields_list):
        directory_mf = self.env["physical.directory.mf"].search([("id", '=', fields_list["directory_mf"])], None, 1)
        fields_list["last_modification_date_mf"] = self.get_last_modification_date(
            directory_mf.path_mf, fields_list["name"]
        )
        fields_list["content_mf"] = base64.b64encode(
            self.get_content(directory_mf.path_mf, fields_list["name"])
        )
        return super(PhysicalFileMF, self).create(fields_list)

    @staticmethod
    def get_content(directory_path, file_name):
        file = open(os.path.join(directory_path, file_name), "rb")
        return file.read()

    @staticmethod
    def get_last_modification_date(directory_path, file_name):
        last_modification_timestamp = os.path.getmtime(os.path.join(directory_path, file_name))
        return datetime.fromtimestamp(last_modification_timestamp).strftime('%Y-%m-%d %H:%M:%S')

    @api.multi
    def delete(self):
        file_path = os.path.join(self.directory_mf.path_mf, self.name)
        if os.path.exists(file_path):
            os.remove(file_path)
            self.unlink()
            # Reload view to update files list
            return {'type': 'ir.actions.act_window_view_reload'}
