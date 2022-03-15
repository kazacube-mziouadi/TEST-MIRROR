from openerp import models, fields, api, _
import datetime
from openerp.exceptions import MissingError
import pytz


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
    use_custom_extension = fields.Boolean(string="Name files with a custom extension", default=False)
    custom_extension = fields.Char(string="Custom extension")

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.one
    def launch(self):
        if not self.model_dictionaries_to_export_mf:
            raise MissingError("You must configure the models to export before being able to launch the export.")
        for model_dictionary in self.model_dictionaries_to_export_mf:
            self.export_model_dictionary(model_dictionary)

    def export_model_dictionary(self, model_dictionary):
        start_datetime = datetime.datetime.now()
        file_name = self.get_file_name()
        records_to_export_list = self.env["exporter.service.mf"].get_records_to_export_list_from_model_dictionary(
            model_dictionary
        )
        if self.file_extension_mf in ["csv", "txt"]:
            fields_names_list = model_dictionary.get_fields_names_list()
        else:
            fields_names_list = None
        file_content = self.env["converter.service.mf"].convert_models_list_to_file_content(
            records_to_export_list, self.file_extension_mf, self.file_separator_mf, self.file_quoting_mf, fields_names_list
        )
        if self.activate_file_generation_mf:
            self.directory_mf.write({
                "files_mf": [(0, 0, {
                    "name": file_name,
                    "content_mf": file_content
                })]
            })
        export_attempt_file = self.env["file.mf"].create({
            "name": file_name,
            "content_mf": file_content
        })
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

    def get_file_name(self):
        company_timezone = pytz.timezone(self.env.user.company_id.tz)
        now_formatted = company_timezone.fromutc(datetime.datetime.now()).strftime("%Y%m%d_%H%M%S")
        if self.use_custom_extension:
            extension = ('.' if not self.custom_extension.startswith('.') else '') + self.custom_extension
        else:
            extension = '.' + self.file_extension_mf
        return "MFFI-Export-" + now_formatted + extension

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
