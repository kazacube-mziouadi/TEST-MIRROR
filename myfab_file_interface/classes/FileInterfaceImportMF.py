# -*- coding: utf-8 -*-
from openerp import models, fields, api, registry, _
import traceback
import base64
from openerp.exceptions import MissingError
import json

KEYS_IN_IMPORT_DICT = ["method", "fields", "write", "callback", "model", "status", "reference", "committed"]


class FileInterfaceImportMF(models.Model):
    _inherit = "file.interface.mf"
    _name = "file.interface.import.mf"
    _description = "myfab file interface import configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    import_attempts_mf = fields.One2many("file.interface.import.attempt.mf", "file_interface_import_mf",
                                         string="Import attempts", readonly=True)
    file_encoding_mf = fields.Selection(
        [("utf-8", "UTF-8"), ("cp1252", "CP1252")], "File encoding", default="utf-8", required=True
    )

    # ===========================================================================
    # METHODS - IMPORT PROCESSING
    # ===========================================================================

    @api.one
    def launch(self):
        if self.directory_mf.directory_scan_is_needed_mf:
            self.directory_mf.mf_scan_directory()
        sorted_files_list = sorted(self.directory_mf.files_mf, key=lambda file_mf: file_mf.sequence)
        for file_to_import in sorted_files_list:
            #Add the context to help all search/create function with trads, else it doesn't find all wanted elements
            self.with_context(lang=self.env.user.lang).import_file(
                base64.b64decode(file_to_import.content_mf), file_to_import.name
            )
            self.env.cr.commit()

    def import_file(self, file_content, file_name):
        import_attempt_file = self.env["file.mf"].create({
            "name": file_name,
            "content_mf": file_content
        })
        import_attempt_dict = {
            "start_datetime_mf": self.get_current_datetime(),
            "file_name_mf": file_name,
            "file_mf": import_attempt_file.id
        }
        records_to_process_list = []
        try:
            records_to_process_list = self.env["parser.service.mf"].get_records_from_file(
                self.file_extension_mf, file_content, file_name, self.file_separator_mf, self.file_quoting_mf,
                self.file_encoding_mf
            )
            self.env["importer.service.mf"].import_records_list(records_to_process_list)
        except Exception as e:
            record_import_failed_dict = None
            if len(e.args) == 3:
                exception, exception_traceback, record_import_failed_dict = e
            else:
                exception_traceback = traceback.format_exc()

            # Rollback du curseur de l'ORM (pour supprimer les injections en cours + refaire des requetes dessous)
            self.env.cr.rollback()
            # Creation du fichier de tentative non factorisable a cause du rollback ci-dessus
            import_attempt_file = self.env["file.mf"].create({
                "name": file_name,
                "content_mf": file_content
            })
            # Creation de la tentative
            import_attempt_dict.update({
                "is_successful_mf": False,
                "end_datetime_mf": self.get_current_datetime(),
                "file_mf": import_attempt_file.id
            })
            if type(records_to_process_list) is list :
                incorrect_file_key = self.get_incorrect_dict_key_in_records_dicts_list(records_to_process_list)
                if incorrect_file_key:
                    # Si on arrive ici c'est qu'il y a une clé incorrecte dans le fichier, on la signale explicitement
                    import_attempt_dict.update({
                        "message_mf": _("The following key found in the file is incorrect : " + incorrect_file_key)
                    })
                else:
                    # Gestion des exceptions "classiques"
                    import_attempt_dict.update({
                        "message_mf": exception_traceback,
                        "record_imports_mf": self.get_one2many_record_imports_creation_list_from_dicts_list(
                            records_to_process_list, record_import_failed_dict
                        ),
                    })
            else:
                # Si on arrive ici c'est que le format du fichier est incorrect, on le signale explicitement
                import_attempt_dict.update({
                    "message_mf": _("The file's structure is incorrect.")
                })
            self.write({"import_attempts_mf": [(0, 0, import_attempt_dict)]})
            self.directory_mf.mf_delete_file(file_name)
            # On arrete l'import ici
            return
        # Creation de la tentative
        import_attempt_dict.update({
            "is_successful_mf": True,
            "end_datetime_mf": self.get_current_datetime(),
            "message_mf": _("Import successful."),
            "record_imports_mf": self.get_one2many_record_imports_creation_list_from_dicts_list(records_to_process_list)
        })
        self.write({"import_attempts_mf": [(0, 0, import_attempt_dict)]})
        self.directory_mf.mf_delete_file(file_name)

    @staticmethod
    def get_incorrect_dict_key_in_records_dicts_list(records_dicts_list):
        for record_dict in records_dicts_list:
            for record_dict_key in record_dict.keys():
                if record_dict_key not in KEYS_IN_IMPORT_DICT:
                    return record_dict_key
        return False

    def get_one2many_record_imports_creation_list_from_dicts_list(self, records_list, record_import_failed_dict=None):
        import_attempt_record_imports_list = []
        for record_dict in records_list:
            record_import_model = self.env["ir.model"].search(
                [("model", '=', record_dict["model"])], None, 1
            )
            import_rows_to_create_list = []
            if "rows" in record_dict:
                for row_dict in record_dict["rows"]:
                    import_rows_to_create_list.append((0, 0, {
                        "row_number_mf": row_dict["row_number"],
                        "row_content_mf": row_dict["row_content"]
                    }))
            record_import_dict = {
                "method_mf": record_dict["method"],
                "model_mf": record_import_model.id,
                "record_import_rows_mf": import_rows_to_create_list,
                "fields_mf": json.dumps(record_dict["fields"], sort_keys=True, indent=4),
                "fields_to_write_mf": record_dict["write"] if "write" in record_dict else "",
                "callback_method_mf": record_dict["callback"] if "callback" in record_dict else "",
                "committed_mf": record_dict["committed"] if "committed" in record_dict else False,
                "mf_linked_record_reference": self.format_reference(record_import_model, record_dict["reference"]) if "reference" in record_dict else False
            }
            if record_import_failed_dict and record_dict == record_import_failed_dict:
                record_import_dict["status_mf"] = "failed"
            else:
                record_import_dict["status_mf"] = record_dict["status"] if "status" in record_dict else "not processed"
            import_attempt_record_imports_list.append((0, 0, record_import_dict))
        return import_attempt_record_imports_list

    @staticmethod
    def format_reference(model_id, reference_raw):
        if reference_raw:
            return model_id.model + ',' + str(reference_raw[0].id)

    # ===========================================================================
    # METHODS - BUTTONS
    # ===========================================================================

    @api.one
    def launch_button(self):
        if self.directory_mf.directory_scan_is_needed_mf:
            self.directory_mf.mf_scan_directory()
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
                raise MissingError(_("No files found in directory ") + self.directory_path_mf)
            self.launch()

    @api.one
    def open_upload_import_file_wizard(self):
        self.directory_mf._is_dir_valid()
        return {
            "name": _("Upload import file into directory"),
            "view_mode": "form",
            "res_model": "wizard.upload.file.mf",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"directory_id": self.directory_mf.id}
        }
