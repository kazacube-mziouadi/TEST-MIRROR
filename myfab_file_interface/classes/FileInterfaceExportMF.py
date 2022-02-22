from openerp import models, fields, api, _
import datetime
import base64


class FileInterfaceExportMF(models.Model):
    _inherit = "file.interface.mf"
    _name = "file.interface.export.mf"
    _description = "MyFab file interface export configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    model_dictionaries_to_export_mf = fields.One2many("file.interface.export.model.dictionary.mf",
                                                      "file_interface_export_mf",
                                                      string="Models to Export", ondelete="cascade")
    activate_file_generation_mf = fields.Boolean(string="Activate file generation", default=True)
    export_attempts_mf = fields.One2many("file.interface.export.attempt.mf", "file_interface_export_mf",
                                         string="Export attempts", ondelete="cascade", readonly=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.one
    def launch(self):
        if not self.is_ready_to_launch():
            return
        start_datetime = datetime.datetime.now()
        file_name = self.get_file_name()
        exporter_service = self.env["exporter.service.mf"].create({})
        converter_service = self.env["converter.service.mf"].create({})
        records_to_export_list = exporter_service.format_records_to_export_to_list(self.model_dictionaries_to_export_mf)
        if self.file_extension_mf in ["csv", "txt"]:
            fields_names_list = self.model_dictionaries_to_export_mf[0].get_fields_names_list()
        else:
            fields_names_list = None
        # TODO : csv/txt n'exportent que le premier Model Dictionary => boucler pour generer un fichier par modele dict
        file_content = converter_service.convert_models_list_to_file_content(
            records_to_export_list, self.file_extension_mf, self.file_separator_mf, self.file_quoting_mf, fields_names_list
        )
        export_file_dict = {
            "name": file_name,
            "content_mf": file_content
        }
        if self.activate_file_generation_mf:
            self.directory_mf.write({
                "files_mf": [(0, 0, export_file_dict)]
            })
        export_attempt_file = self.env["file.mf"].create(export_file_dict)
        self.write({
            "export_attempts_mf": [(0, 0, {
                "start_datetime_mf": start_datetime,
                "file_name_mf": file_name,
                "end_datetime_mf": datetime.datetime.now(),
                "message_mf": "Export successful.",
                "is_successful_mf": True,
                "file_mf": export_attempt_file.id
            })]
        })

    def is_ready_to_launch(self):
        return self.model_dictionaries_to_export_mf

    def get_file_name(self):
        now_formatted = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y%m%d_%H%M%S")
        return "MFFI-Export-" + now_formatted + '.' + self.file_extension_mf

    @api.multi
    def generate_cron_for_export(self):
        return {
            "name": _("Generate cron for export"),
            "view_mode": "form",
            "res_model": "wizard.file.interface.cron.mf",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {
                "record_model_name_mf": "file.interface.export.mf",
                "record_name_mf": self.name,
                "record_id_mf": self.id,
                "record_method_mf": "export_records"
            }
        }

    @api.multi
    def delete_cron_for_export(self):
        self.env["ir.cron"].search([
            ("model", "=", "file.interface.export.mf"),
            ("function", "=", "export_records"),
            ("args", "=", repr([self.id]))
        ], None, 1).unlink()
