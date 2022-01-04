from openerp import models, fields, api, registry, _
import traceback
import base64


class FileInterfaceImportMF(models.Model):
    _inherit = "file.interface.mf"
    _name = "file.interface.import.mf"
    _description = "MyFab file interface import configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    import_attempts_mf = fields.One2many("file.interface.import.attempt.mf", "file_interface_import_mf",
                                         string="Import attempts", ondelete="cascade", readonly=True)
    file_encoding_mf = fields.Selection(
        [("utf-8", "UTF-8"), ("cp1252", "CP1252")], "File encoding", default="utf-8", required=True
    )

    # ===========================================================================
    # METHODS - IMPORT PROCESSING
    # ===========================================================================

    @api.one
    def launch(self):
        if self.directory_mf.directory_scan_is_needed_mf:
            self.directory_mf.scan_directory()
        parser_service = self.env["parser.service.mf"].create({})
        importer_service = self.env["importer.service.mf"].create({})
        for file_to_import in self.directory_mf.files_mf:
            self.import_file(
                parser_service, importer_service, base64.b64decode(file_to_import.content_mf), file_to_import.name
            )

    def import_file(self, parser_service, importer_service, file_content, file_name):
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
            records_to_process_list = parser_service.get_records_from_file(
                self.file_extension_mf, file_content, file_name, self.file_separator_mf, self.file_quoting_mf,
                self.file_encoding_mf
            )
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
            self.directory_mf.delete_file(file_name)
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
        self.directory_mf.delete_file(file_name)
        self.env.cr.commit()

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
    def launch_button(self):
        if self.directory_mf.directory_scan_is_needed_mf:
            self.directory_mf.scan_directory()
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
            if not self.directory_mf.files_mf:
                return {
                    "name": _("No file to import in the import directory"),
                    "view_mode": "form",
                    "res_model": "wizard.no.import.file.mf",
                    "type": "ir.actions.act_window",
                    "target": "new",
                    "context": {}
                }
            self.launch()

    @api.one
    def open_upload_import_file_wizard(self):
        return {
            "name": _("Upload import file into directory"),
            "view_mode": "form",
            "res_model": "wizard.upload.file.mf",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"directory_id": self.directory_mf.id}
        }
