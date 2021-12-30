from openerp import models, fields, api, registry, _
import os
import traceback
from datetime import datetime
import base64
from openerp.addons.myfab_file_interface.classes.files.PhysicalFileMF import PhysicalFileMF


class FileInterfaceImportMF(models.Model):
    _name = "file.interface.import.mf"
    _description = "MyFab file interface import configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=True, help='')
    import_directory_path_mf = fields.Char(string="Import directory path",
                                           default="/etc/openprod_home/MyFabFileInterface/Imports")
    cron_already_exists_mf = fields.Boolean(compute="_compute_cron_already_exists", readonly=True)
    file_extension_mf = fields.Selection(
        [("json", "JSON"), ("csv", "CSV"), ("txt", "TXT")], "File extension", default=("json", "JSON"), required=True
    )
    file_separator_mf = fields.Char(string="File data separator", default=",")
    file_quoting_mf = fields.Char(string="File data quoting", default='"')
    file_encoding_mf = fields.Selection(
        [("utf-8", "UTF-8"), ("cp1252", "CP1252")], "File encoding", default=("utf-8", "UTF-8"), required=True
    )
    import_attempts_mf = fields.One2many("file.interface.import.attempt.mf", "file_interface_import_mf",
                                         string="Import attempts", ondelete="cascade", readonly=True)
    files_to_import_mf = fields.One2many("file.interface.import.file.to.import.mf", "file_interface_import_mf",
                                         string="Files to import", ondelete="cascade", readonly=True)
    files_to_import_scan_is_needed_mf = fields.Boolean(compute="_compute_files_to_import_scan_is_needed", readonly=True)

    # ===========================================================================
    # METHODS - COMPUTE
    # ===========================================================================

    @api.one
    def _compute_cron_already_exists(self):
        existing_crons = self.env["ir.cron"].search([
            ("model", "=", "file.interface.import.mf"),
            ("function", "=", "import_files"),
            ("args", "=", repr([self.id]))
        ], None, 1)
        if len(existing_crons) > 0:
            self.cron_already_exists_mf = True
        else:
            self.cron_already_exists_mf = False

    @api.one
    def _compute_files_to_import_scan_is_needed(self):
        files_names_list = self.get_files_to_import_names_list()
        if len(files_names_list) != len(self.files_to_import_mf):
            self.files_to_import_scan_is_needed_mf = True
            return
        for file_to_import in self.files_to_import_mf:
            file_to_import_is_up_to_date = False
            for physical_file_name in files_names_list:
                if self.is_file_to_import_corresponding_to_physical_file(file_to_import, physical_file_name):
                    file_to_import_is_up_to_date = True
                    continue
            if not file_to_import_is_up_to_date:
                self.files_to_import_scan_is_needed_mf = True
                return
        self.files_to_import_scan_is_needed_mf = False

    # ===========================================================================
    # METHODS - FILES TO IMPORT LIST MANAGEMENT
    # ===========================================================================

    def is_file_to_import_corresponding_to_physical_file(self, file_to_import, physical_file_name):
        physical_file_last_modification_date = PhysicalFileMF.get_last_modification_date(
            self.import_directory_path_mf, physical_file_name
        )
        return file_to_import.name == physical_file_name and (
            file_to_import.last_modification_date_mf == physical_file_last_modification_date
        )

    @api.one
    def scan_files_to_import(self):
        # Emptying current files to import list
        for file_to_import in self.files_to_import_mf:
            file_to_import.unlink()
        files_names_list = self.get_files_to_import_names_list()
        files_to_import_list = [(0, 0, {
            "name": file_name,
            "directory_path_mf": self.import_directory_path_mf,
            "content_mf": base64.b64encode(PhysicalFileMF.get_content(self.import_directory_path_mf, file_name)),
            "last_modification_date_mf": PhysicalFileMF.get_last_modification_date(
                self.import_directory_path_mf, file_name
            )
        }) for file_name in files_names_list]
        self.write({
            "files_to_import_mf": files_to_import_list
        })

    def get_files_to_import_names_list(self):
        files_to_import_names_list = [
            file_name for file_name in os.listdir(self.import_directory_path_mf)
            if os.path.isfile(os.path.join(self.import_directory_path_mf, file_name))
        ]
        files_to_import_names_list.sort()
        return files_to_import_names_list

    def delete_import_file(self, file_name):
        for file_to_import in self.files_to_import_mf:
            if file_to_import.name == file_name:
                file_to_import.delete()
                return

    # ===========================================================================
    # METHODS - IMPORT PROCESSING
    # ===========================================================================

    @api.one
    def import_files(self):
        if self.files_to_import_scan_is_needed_mf:
            self.scan_files_to_import()
        importer_service = self.env["importer.service.mf"].create({})
        for file_to_import in self.files_to_import_mf:
            self.import_file(importer_service, base64.b64decode(file_to_import.content_mf), file_to_import.name)

    def import_file(self, importer_service, file_content, file_name):
        import_attempt_dict = {
            "start_datetime_mf": self.get_current_datetime(),
            "file_name_mf": file_name
        }
        import_attempt_file_dict = {
            "name": file_name
        }
        records_to_process_list = []
        try:
            import_attempt_file_dict["content_mf"] = base64.b64encode(file_content)
            records_to_process_list = self.get_records_by_file_extension(self.file_extension_mf, file_content,
                                                                         file_name)
            importer_service.import_records_list(records_to_process_list)
        except Exception as e:
            record_import_failed_dict = None
            if len(e.args) > 1:
                exception, record_import_failed_dict = e
            exception_traceback = traceback.format_exc()
            # Rollback du curseur de l'ORM (pour supprimer les injections en cours + refaire des requetes dessous)
            self.env.cr.rollback()
            import_attempt_record_imports = self.get_one2many_record_imports_creation_list_from_dicts_list(
                records_to_process_list, record_import_failed_dict
            )
            # Creation de la tentative
            import_attempt_file = self.env["file.mf"].create(import_attempt_file_dict)
            import_attempt_dict.update({
                "is_successful_mf": False,
                "end_datetime_mf": self.get_current_datetime(),
                "message_mf": exception_traceback,
                "record_imports_mf": import_attempt_record_imports,
                "file_mf": import_attempt_file.id
            })
            self.write({"import_attempts_mf": [(0, 0, import_attempt_dict)]})
            # Commit du curseur (necessaire pour sauvegarder les modifs avant de declencher l'erreur)
            self.env.cr.commit()
            self.delete_import_file(file_name)
            # On arrete l'import ici
            return
        import_attempt_file = self.env["file.mf"].create(import_attempt_file_dict)
        import_attempt_dict.update({
            "end_datetime_mf": self.get_current_datetime(),
            "message_mf": "Import successful.",
            "is_successful_mf": True,
            "file_mf": import_attempt_file.id,
            "record_imports_mf": self.get_one2many_record_imports_creation_list_from_dicts_list(records_to_process_list)
        })
        self.write({"import_attempts_mf": [(0, 0, import_attempt_dict)]})
        self.delete_import_file(file_name)
        self.env.cr.commit()

    @staticmethod
    def get_current_datetime():
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

    def get_records_by_file_extension(self, file_extension, file_content, file_name):
        parser_service = self.env["parser.service.mf"].create({})
        if file_extension == "json":
            return parser_service.get_records_from_json(file_content)
        elif file_extension == "csv":
            return parser_service.get_records_from_csv(
                file_content, file_name, self.file_separator_mf, self.file_quoting_mf, self.file_encoding_mf
            )
        elif file_extension == "txt":
            return parser_service.get_records_from_txt(file_content, file_name, self.file_quoting_mf, self.file_encoding_mf)
        raise ValueError("The " + file_extension + " file extension is not supported.")

    def get_one2many_record_imports_creation_list_from_dicts_list(self, records_list, record_import_failed_dict=None):
        import_attempt_record_imports = []
        for record_dict in records_list:
            record_import_model = self.env["ir.model"].search(
                [("model", '=', record_dict["model"])], None, 1
            )
            record_import_dict = {
                "method_mf": record_dict["method"],
                "model_mf": record_import_model.id,
                "fields_mf": record_dict["fields"],
                "fields_to_write_mf": record_dict["write"] if "write" in record_dict else "",
                "callback_method_mf": record_dict["callback"] if "callback" in record_dict else "",
                "committed_mf": record_dict["committed"] if "committed" in record_dict else False
            }
            if record_import_failed_dict and record_dict == record_import_failed_dict:
                record_import_dict["status_mf"] = "failed"
            else:
                record_import_dict["status_mf"] = record_dict["status"] if "status" in record_dict else "not processed"
            import_attempt_record_imports.append((0, 0, record_import_dict))
        return import_attempt_record_imports

    # ===========================================================================
    # METHODS - BUTTONS
    # ===========================================================================

    @api.one
    def import_files_button(self):
        if self.files_to_import_scan_is_needed_mf:
            self.scan_files_to_import()
            return {
                "name": _("The files to import list has been updated"),
                "view_mode": "form",
                "res_model": "wizard.confirm.import.file.mf",
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {
                    "file_interface_import_id": self.id
                }
            }
        else:
            if not self.files_to_import_mf:
                return {
                    "name": _("No file to import in the import directory"),
                    "view_mode": "form",
                    "res_model": "wizard.no.import.file.mf",
                    "type": "ir.actions.act_window",
                    "target": "new",
                    "context": {}
                }
            self.import_files()

    @api.multi
    def generate_cron_for_import(self):
        return {
            "name": _("Generate cron for import"),
            "view_mode": "form",
            "res_model": "wizard.file.interface.cron.mf",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {
                "record_model_name_mf": "file.interface.import.mf",
                "record_name_mf": self.name,
                "record_id_mf": self.id,
                "record_method_mf": "import_files"
            }
        }

    @api.multi
    def delete_cron_for_import(self):
        self.env["ir.cron"].search([
            ("model", "=", "file.interface.import.mf"),
            ("function", "=", "import_files"),
            ("args", "=", repr([self.id]))
        ], None, 1).unlink()

    @api.multi
    def open_upload_import_file_wizard(self):
        return {
            "name": _("Upload import file into import directory"),
            "view_mode": "form",
            "res_model": "wizard.upload.import.file.mf",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"file_interface_import_id": self.id}
        }
