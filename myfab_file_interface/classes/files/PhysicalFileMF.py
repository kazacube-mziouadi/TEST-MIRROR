from openerp import models, fields, api, registry, _
import os
from datetime import datetime


class PhysicalFileMF(models.TransientModel):
    _inherit = "file.mf"
    _name = "physical.file.mf"
    _description = "myfab physical file"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    last_modification_date_mf = fields.Datetime(string="Last modification date")
    directory_mf = fields.Many2one("physical.directory.mf", string="Directory")
    path_mf = fields.Char(compute="_compute_path", string="Absolute path", readonly=True)
    flag = fields.Boolean(string="Flag",default=False)
    
    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.one
    def _compute_path(self):
        self.path_mf = os.path.join(self.directory_mf.path_mf, self.name)

    @api.model
    def create(self, fields_list):
        directory_mf = self.env["physical.directory.mf"].search([("id", '=', fields_list["directory_mf"])], None, 1)
        file_path = os.path.join(directory_mf.path_mf, fields_list["name"])
        
        if self.mf_file_exists(file_path):
            fields_list["content_mf"] = self.mf_read_physical_file(file_path)
            if not fields_list["content_mf"]: return False
        elif not self.mf_append_to_physical_file(file_path, fields_list["content_mf"]): 
            return False

        fields_list["last_modification_date_mf"] = self.mf_get_last_modification_date(file_path)
        if not fields_list["last_modification_date_mf"]: return False
        
        res = super(PhysicalFileMF, self).create(fields_list)
        return res

    @api.multi
    def delete(self):
        file_path = self.path_mf
        if self.mf_file_exists(file_path):
            try:
                os.remove(file_path)
                are_files_deleted = True
            except:
                are_files_deleted = False

            if are_files_deleted: 
                self.unlink()
            # Reload view to update files list
            return {'type': 'ir.actions.act_window_view_reload'}

    @staticmethod
    def mf_file_exists(file_path):
        try:
            return os.path.exists(file_path)
        except:
            return False

    @staticmethod
    def mf_read_physical_file(file_path):
        try:
            file = open(os.path.join(file_path), "rb")
            return file.read()
        except:
            return False

    @staticmethod
    def mf_append_to_physical_file(file_path, file_content):
        file_path = os.path.join(file_path)
        try:
            file = open(file_path, "a")
            file.write(file_content)
            file.close()
            return True
        except:
            return False

    @staticmethod
    def mf_get_last_modification_date(file_path):
        try:
            last_modification_timestamp = os.path.getmtime(os.path.join(file_path))
            return datetime.fromtimestamp(last_modification_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return False
