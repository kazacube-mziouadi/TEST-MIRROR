from openerp import models, fields, api, registry, _
import os
from PhysicalFileMF import PhysicalFileMF


class PhysicalDirectoryMF(models.Model):
    _name = "physical.directory.mf"
    _description = "MyFab physical directory"
    _sql_constraints = [
        (
            "path_unique_mf",
            "UNIQUE(path_mf)",
            "The directory's path must be unique"
        )
    ]

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=128)
    path_mf = fields.Char(string="Directory path", default="/etc/openprod_home/MyFabFileInterface", required=True)
    files_mf = fields.One2many("physical.file.mf", "directory_mf", string="Files", readonly=True)
    directory_scan_is_needed_mf = fields.Boolean(compute="_compute_directory_scan_is_needed", readonly=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.model
    def create(self, fields_list):
        fields_list["name"] = os.path.basename(fields_list["path_mf"])
        return super(PhysicalDirectoryMF, self).create(fields_list)

    @api.one
    def _compute_directory_scan_is_needed(self):
        if not os.path.exists(self.path_mf):
            os.makedirs(self.path_mf)
            self.directory_scan_is_needed_mf = False
            # No need to go further : we just created the directory so it is empty
            return
        files_names_list = self.get_names_list_of_files_physically_in_directory()
        if len(files_names_list) != len(self.files_mf):
            self.directory_scan_is_needed_mf = True
            return
        for related_file in self.files_mf:
            related_file_is_up_to_date = False
            # TODO : trier d'abord les listes sur le nom puis comparer les deux listes sur l'index
            for physical_file_name in files_names_list:
                if self.is_related_file_corresponding_to_physical_file(related_file, physical_file_name):
                    related_file_is_up_to_date = True
                    break
            if not related_file_is_up_to_date:
                self.directory_scan_is_needed_mf = True
                return
        self.directory_scan_is_needed_mf = False

    def is_related_file_corresponding_to_physical_file(self, related_file, physical_file_name):
        physical_file_last_modification_date = PhysicalFileMF.get_last_modification_date(
            os.path.join(self.path_mf, physical_file_name)
        )
        return related_file.name == physical_file_name and (
            related_file.last_modification_date_mf == physical_file_last_modification_date
        )

    @api.one
    def scan_directory(self):
        # Emptying current files list
        for related_file in self.files_mf:
            related_file.unlink()
        files_names_list = self.get_names_list_of_files_physically_in_directory()
        related_files_list = [(0, 0, {"name": file_name}) for file_name in files_names_list]
        # TODO : ajouter un indicateur sur les fichiers pour dire si l'extension est standard ou non avec l'extension choisie ?
        self.write({
            "files_mf": related_files_list
        })

    def get_names_list_of_files_physically_in_directory(self):
        files_names_list = [
            file_name for file_name in os.listdir(self.path_mf)
            if os.path.isfile(os.path.join(self.path_mf, file_name))
        ]
        files_names_list.sort()
        return files_names_list

    def delete_file(self, file_name):
        for related_file in self.files_mf:
            if related_file.name == file_name:
                related_file.delete()
                return

    @api.multi
    def open_upload_file_wizard(self):
        return {
            "name": _("Upload file into directory"),
            "view_mode": "form",
            "res_model": "wizard.upload.file.mf",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"directory_id": self.id}
        }
