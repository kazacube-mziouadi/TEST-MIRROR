from openerp import models, fields, api, _
import json
import datetime
import os
import base64


class FileInterfaceExportMF(models.Model):
    _name = "file.interface.export.mf"
    _description = "MyFab file interface export configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=True, help='')
    import_directory_path_mf = fields.Char(string="Files path",
                                           default="/etc/openprod_home/MyFabFileInterface/Exports")
    model_dictionaries_to_export_mf = fields.One2many("file.interface.export.model.dictionary.mf",
                                                      "file_interface_export_mf",
                                                      string="Models to Export", ondelete="cascade")
    last_file_generated_mf = fields.Text(string="Last file generated", readonly=True)
    last_file_generated_name_mf = fields.Char(string="Last file generated name", readonly=True)
    cron_already_exists_mf = fields.Boolean(compute="_compute_cron_already_exists", readonly=True)
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
        if len(existing_crons) > 0:
            self.cron_already_exists_mf = True
        else:
            self.cron_already_exists_mf = False

    @api.one
    def export_records(self):
        exporter_service = self.env["exporter.service.mf"].create({})
        json_content_dict = exporter_service.format_models_to_export_to_dict(self.model_dictionaries_to_export_mf)
        json_content = json.dumps(json_content_dict, sort_keys=True, indent=4)
        if self.activate_file_generation_mf:
            self.write_myfab_file_interface_file_file(json_content)
        self.last_file_generated_mf = json_content

    def write_myfab_file_interface_file_file(self, json_content_string):
        now = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y%m%d_%H%M%S")
        if not os.path.exists(self.import_directory_path_mf):
            os.makedirs(self.import_directory_path_mf)
        file_name = "MFFI-Export-" + now + ".json"
        file_path = os.path.join(self.import_directory_path_mf, file_name)
        file = open(file_path, "a")
        file.write(json_content_string)
        file.close()
        self.last_file_generated_name_mf = file_name

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
