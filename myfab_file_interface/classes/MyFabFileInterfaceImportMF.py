from openerp import models, fields, api, registry, _
import os
import sys
import traceback


class MyFabFileInterfaceImportMF(models.Model):
    _name = "myfab.file.interface.import.mf"
    _description = "MyFab file interface import configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=True, help='')
    import_directory_path_mf = fields.Char(string="Files path", default="/etc/openprod_home/MyFabFileInterface/Imports")
    cron_already_exists_mf = fields.Boolean(compute="_compute_cron_already_exists", readonly=True)
    last_data_imported_mf = fields.Text(string="Last data imported", readonly=True)
    last_import_error_mf = fields.Char(string="Last import error", readonly=True)
    last_import_success_mf = fields.Boolean(default=True)
    file_extension_mf = fields.Selection(
        [("json", "JSON"), ("csv", "CSV"), ("txt", "TXT")], "File extension", default=("json", "JSON"), required=True
    )
    file_separator_mf = fields.Char(string="File data separator", default=",")
    file_quoting_mf = fields.Char(string="File data quoting", default='"')
    file_encoding_mf = fields.Selection(
        [("utf-8", "UTF-8"), ("cp1252", "CP1252")], "File encoding", default=("utf-8", "UTF-8"), required=True
    )

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.one
    def _compute_cron_already_exists(self):
        existing_crons = self.env["ir.cron"].search([
            ("model", "=", "myfab.file.interface.import.mf"),
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
        for file_name in files:
            try:
                self.import_file(file_name)
            except Exception as e:
                exception = e
                exception_traceback = traceback.format_exc()
                # Archivage du fichier dans le dossier Erreurs et creation du fichier de log
                self.archive_file(file_name, "Erreurs")
                self.write_error_log_file(file_name, exception_traceback)
                # Rollback du curseur de l'ORM (pour supprimer les injections en cours + refaire des requetes dessous)
                self.env.cr.rollback()
                # Injection de l'erreur dans le champ last_import_error_mf du file pour affichage
                self.last_import_error_mf = exception_traceback
                self.last_import_success_mf = False
                # Commit du curseur (necessaire pour sauvegarder les modifs avant de declencher l'erreur)
                self.env.cr.commit()
                # Declenchement de l'erreur
                sys.exit(exception)
            self.archive_file(file_name, "Archives")
        self.last_import_success_mf = True

    def import_file(self, file_name):
        file = open(os.path.join(self.import_directory_path_mf, file_name), "rb")
        file_content = file.read()
        self.last_data_imported_mf = file_content
        records_to_process_list = self.get_records_by_file_extension(self.file_extension_mf, file_content, file_name)
        importer_service = self.env["importer.service.mf"].create({})
        importer_service.import_records_list(records_to_process_list)

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
        raise ValueError("The given file extension isn't processable.")

    def archive_file(self, file_name, directory_name):
        archive_path = os.path.join(self.import_directory_path_mf, directory_name)
        if not os.path.exists(archive_path):
            os.makedirs(archive_path)
        os.rename(os.path.join(self.import_directory_path_mf, file_name), os.path.join(archive_path, file_name))

    @api.multi
    def generate_cron_for_import(self):
        return {
            'name': _("Generate cron for import"),
            'view_mode': 'form',
            'res_model': 'wizard.myfab.file.interface.cron.mf',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'object_model_name_mf': "myfab.file.interface.import.mf",
                'object_name_mf': self.name,
                'object_id_mf': self.id,
                'object_method_mf': "import_files"
            }
        }

    @api.multi
    def delete_cron_for_import(self):
        self.env["ir.cron"].search([
            ("model", "=", "myfab.file.interface.import.mf"),
            ("function", "=", "import_files"),
            ("args", "=", repr([self.id]))
        ], None, 1).unlink()

    @api.multi
    def open_upload_import_file_wizard(self):
        return {
            'name': _("Upload import file into import directory"),
            'view_mode': 'form',
            'res_model': 'wizard.upload.import.file.mf',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'upload_directory_mf': self.import_directory_path_mf}
        }

    def write_error_log_file(self, failed_file_name, error_content_string):
        error_directory_path = os.path.join(self.import_directory_path_mf, "Erreurs")
        if not os.path.exists(error_directory_path):
            os.makedirs(error_directory_path)
        log_file_name = failed_file_name + ".log"
        self.write_file(error_directory_path, log_file_name, error_content_string)

    @staticmethod
    def write_file(directory_path, file_name, content):
        file_path = os.path.join(directory_path, file_name)
        file = open(file_path, "a")
        file.write(content)
        file.close()
