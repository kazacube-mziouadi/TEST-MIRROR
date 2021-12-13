from openerp import models, fields, api, registry, _
import os
import sys
import traceback
import datetime
import base64


class FileInterfaceImportMF(models.Model):
    _name = "file.interface.import.mf"
    _description = "MyFab file interface import configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=True, help='')
    import_directory_path_mf = fields.Char(string="Files path", default="/etc/openprod_home/MyFabFileInterface/Imports")
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

    # ===========================================================================
    # METHODS
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
    def import_files(self):
        files = [
            f for f in os.listdir(self.import_directory_path_mf)
            if os.path.isfile(os.path.join(self.import_directory_path_mf, f))
        ]
        importer_service = self.env["importer.service.mf"].create({})
        files.sort()
        for file_name in files:
            file = open(os.path.join(self.import_directory_path_mf, file_name), "rb")
            file_content = file.read()
            try:
                self.import_file(importer_service, file_content, file_name)
            except Exception as e:
                return {'type': 'ir.actions.act_window_view_reload'}
        return {'type': 'ir.actions.act_window_view_reload'}

    def import_file(self, importer_service, file_content, file_name):
        import_attempt_values_dict = {
            "start_datetime_mf": self.get_current_time(),
            "file_name_mf": file_name
        }
        records_to_process_list = []
        try:
            import_attempt_values_dict["file_content_mf"] = base64.b64encode(file_content)
            records_to_process_list = self.get_records_by_file_extension(self.file_extension_mf, file_content,
                                                                         file_name)
            importer_service.import_records_list(records_to_process_list)
        except Exception as e:
            record_import_failed_dict = None
            if len(e.args) > 1:
                exception, record_import_failed_dict = e
            else:
                exception = e
            exception_traceback = traceback.format_exc()
            # Rollback du curseur de l'ORM (pour supprimer les injections en cours + refaire des requetes dessous)
            self.env.cr.rollback()
            import_attempt_record_imports = self.get_one2many_record_imports_creation_list_from_dicts_list(
                records_to_process_list, record_import_failed_dict
            )
            # Creation de la tentative
            import_attempt_values_dict.update({
                "is_successful_mf": False,
                "end_datetime_mf": self.get_current_time(),
                "message_mf": exception_traceback,
                "record_imports_mf": import_attempt_record_imports
            })
            self.write({"import_attempts_mf": [(0, 0, import_attempt_values_dict)]})
            # Commit du curseur (necessaire pour sauvegarder les modifs avant de declencher l'erreur)
            self.env.cr.commit()
            self.delete_import_file(file_name)
            # Declenchement de l'erreur
            sys.exit(exception)
        import_attempt_values_dict.update({
            "end_datetime_mf": self.get_current_time(),
            "message_mf": "Import successful.",
            "is_successful_mf": True,
            "record_imports_mf": self.get_one2many_record_imports_creation_list_from_dicts_list(records_to_process_list)
        })
        self.write({"import_attempts_mf": [(0, 0, import_attempt_values_dict)]})
        self.delete_import_file(file_name)
        self.env.cr.commit()

    @staticmethod
    def get_current_time():
        return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

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
                [("name", '=', record_dict["model"])], None, 1
            )
            record_import_dict = {
                "method_mf": record_dict["method"],
                "model_mf": record_import_model.id,
                "fields_mf": record_dict["fields"],
                "fields_to_write_mf": record_dict["write"] if "write" in record_dict else ""
            }
            if record_import_failed_dict and record_dict == record_import_failed_dict:
                record_import_dict["status_mf"] = "failed"
            else:
                record_import_dict["status_mf"] = record_dict["status"] if "status" in record_dict else "not processed"
            import_attempt_record_imports.append((0, 0, record_import_dict))
        return import_attempt_record_imports

    def delete_import_file(self, file_name):
        file_path = os.path.join(self.import_directory_path_mf, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

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
            "context": {"upload_directory_mf": self.import_directory_path_mf}
        }
