from openerp import models, fields, api, _
import json
import datetime
import os
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
    def _compute_cron_already_exists(self):
        existing_crons = self.env["ir.cron"].search([
            ("model", "=", "file.interface.export.mf"),
            ("function", "=", "export_records"),
            ("args", "=", repr([self.id]))
        ], None, 1)
        self.cron_already_exists_mf = len(existing_crons) > 0

    @api.one
    def launch(self):
        start_datetime = datetime.datetime.now()
        now_formatted = (start_datetime + datetime.timedelta(hours=2)).strftime("%Y%m%d_%H%M%S")
        file_name = "MFFI-Export-" + now_formatted + ".json"
        exporter_service = self.env["exporter.service.mf"].create({})
        file_content_dict = exporter_service.format_models_to_export_to_dict(self.model_dictionaries_to_export_mf)
        json_content = json.dumps(file_content_dict, sort_keys=True, indent=4)
        if self.activate_file_generation_mf:
            self.create_export_file(file_name, json_content)
        import_attempt_file = self.env["file.mf"].create({
            "name": file_name,
            "content_mf": base64.b64encode(json_content)
        })
        self.write({"export_attempts_mf": [(0, 0, {
            "start_datetime_mf": start_datetime,
            "file_name_mf": file_name,
            "end_datetime_mf": datetime.datetime.now(),
            "message_mf": "Export successful.",
            "is_successful_mf": True,
            "file_mf": import_attempt_file.id
        })]})

    def create_export_file(self, file_name, json_content_string):
        file_path = os.path.join(self.directory_mf.path_mf, file_name)
        file = open(file_path, "a")
        file.write(json_content_string)
        file.close()

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

    @api.one
    def generate_selected_models_import_file(self):
        exporter_service = self.env["exporter.service.mf"].create({})
        json_content_array = exporter_service.format_models_to_import_to_dict(self.model_dictionaries_to_export_mf)
        json_content = json.dumps(json_content_array, sort_keys=True, indent=4)
        now = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y%m%d_%H%M%S")
        return self.env["binary.download"].execute(
            base64.b64encode(json_content),
            "MyFabFileInterface-Import-" + now + ".json"
        )
