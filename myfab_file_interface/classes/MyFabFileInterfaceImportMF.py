from openerp import models, fields, api, _
import json
import datetime
import os


class MyFabFileInterfaceImportMF(models.Model):
    _name = "myfab.file.interface.import.mf"
    _description = "MyFab file interface import configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=True, help='')
    files_path_mf = fields.Char(string="Files path", default="/etc/openprod_home/MyFabFileInterface/Imports/WorkOrders")
    last_json_imported_mf = fields.Text(string="Last JSON imported", readonly=True)
    cron_already_exists_mf = fields.Boolean(compute="_compute_cron_already_exists", readonly=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.one
    def _compute_cron_already_exists(self):
        existing_crons = self.env["ir.cron"].search([
            ("model", "=", "myfab.file.interface.export.mf"),
            ("function", "=", "import_files"),
            ("args", "=", repr([self.id]))
        ], None, 1)
        if len(existing_crons) > 0:
            self.cron_already_exists_mf = True
        else:
            self.cron_already_exists_mf = False

    @api.one
    def import_files(self):
        files = [f for f in os.listdir(self.files_path_mf) if os.path.isfile(os.path.join(self.files_path_mf, f))]
        for file_name in files:
            self.import_file(file_name)

    def import_file(self, file_name):
        file = open(os.path.join(self.files_path_mf, file_name), "r")
        file_content = file.read()
        objects_to_create_array = json.loads(file_content)
        for object_to_create_dictionary in objects_to_create_array:
            self.create_model(object_to_create_dictionary)

    def create_model(self, object_to_create_dictionary):
        for model_name in object_to_create_dictionary:
            self.env[model_name].create(object_to_create_dictionary[model_name])
            print(object_to_create_dictionary[model_name])

    @api.multi
    def generate_cron_for_import(self):
        return {
            'name': _("Generate cron for import"),
            'view_mode': 'form',
            'res_model': 'wizard.myfab.file.interface.import.cron.mf',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'myfab_file_interface_import_id': self.id}
        }

    @api.multi
    def delete_cron_for_import(self):
        self.env["ir.cron"].search([
            ("model", "=", "myfab.file.interface.import.mf"),
            ("function", "=", "import_files"),
            ("args", "=", repr([self.id]))
        ], None, 1).unlink()
