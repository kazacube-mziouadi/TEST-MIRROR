from openerp import models, fields, api, _
import json
import datetime
import os
import base64


class MyFabFileInterfaceExportMF(models.Model):
    _name = "myfab.file.interface.export.mf"
    _description = "MyFab file interface export configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=True, help='')
    import_directory_path_mf = fields.Char(string="Files path",
                                           default="/etc/openprod_home/MyFabFileInterface/Exports/WorkOrders")
    model_to_export_configs_mf = fields.One2many("myfab.file.interface.export.model.export.config.mf",
                                                 "myfab_file_interface_export_mf", string='MyFab Model Export Configs')
    last_json_generated_mf = fields.Text(string="Last JSON generated", readonly=True)
    last_json_generated_name_mf = fields.Char(string="Last JSON generated name", readonly=True)
    cron_already_exists_mf = fields.Boolean(compute="_compute_cron_already_exists", readonly=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.one
    def _compute_cron_already_exists(self):
        existing_crons = self.env["ir.cron"].search([
            ("model", "=", "myfab.file.interface.export.mf"),
            ("function", "=", "export_models"),
            ("args", "=", repr([self.id]))
        ], None, 1)
        if len(existing_crons) > 0:
            self.cron_already_exists_mf = True
        else:
            self.cron_already_exists_mf = False

    @api.one
    def export_models(self):
        json_content_dict = self.format_models_to_export_to_dict()
        json_content = json.dumps(json_content_dict, sort_keys=True, indent=4)
        self.write_myfab_file_interface_json_file(json_content)
        self.last_json_generated_mf = json_content

    def format_models_to_export_to_dict(self):
        content_dict = {}
        for model_to_export_config in self.model_to_export_configs_mf:
            content_dict[model_to_export_config.model_to_export_mf.model] = self.get_dict_of_objects_to_export(
                model_to_export_config
            )
        return content_dict

    def get_dict_of_objects_to_export(self, model_to_export_config):
        list_of_objects_to_export = {}
        objects_to_export = self.env[model_to_export_config.model_to_export_mf.model].search([])
        for object_to_export in objects_to_export:
            list_of_objects_to_export[object_to_export.display_name] = self.get_dict_of_object_to_export(
                object_to_export, model_to_export_config.fields_to_export_mf
            )
        return list_of_objects_to_export

    def get_dict_of_object_to_export(self, object_to_export, fields_to_export):
        object_dict = {}
        for field_to_export in fields_to_export:
            # TODO : function get_field_to_export
            object_field_value = getattr(object_to_export, field_to_export.name)
            if field_to_export.ttype in ["many2many", "one2many"]:
                # List of objects
                for sub_object in object_field_value:
                    # TODO : recursive call
                    pass
            elif field_to_export.ttype == "many2one":
                # object
                pass
            else:
                # string with double quotes
                object_dict[field_to_export.name] = object_field_value
        return object_dict


    def write_myfab_file_interface_json_file(self, json_content_string):
        now = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y%m%d_%H%M%S")
        if not os.path.exists(self.import_directory_path_mf):
            os.makedirs(self.import_directory_path_mf)
        file_name = "MFFI-WorkOrders-" + now + ".json"
        file_path = os.path.join(self.import_directory_path_mf, file_name)
        file = open(file_path, "a")
        file.write(json_content_string)
        file.close()
        self.last_json_generated_name_mf = file_name

    @api.multi
    def generate_cron_for_export(self):
        return {
            'name': _("Generate cron for export"),
            'view_mode': 'form',
            'res_model': 'wizard.myfab.file.interface.cron.mf',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'object_model_name_mf': "myfab.file.interface.export.mf",
                'object_name_mf': self.name,
                'object_id_mf': self.id,
                'object_method_mf': "export_models"
            }
        }

    @api.multi
    def delete_cron_for_export(self):
        self.env["ir.cron"].search([
            ("model", "=", "myfab.file.interface.export.mf"),
            ("function", "=", "export_models"),
            ("args", "=", repr([self.id]))
        ], None, 1).unlink()

    @api.multi
    def download_last_export(self):
        return self.env['binary.download'].execute(
            base64.b64encode(self.last_json_generated_mf),
            self.last_json_generated_name_mf
        )

    @api.multi
    def download_current_export_default_import(self):
        work_orders = self.get_work_orders_to_send_to_myfab_file_interface()
        json_content = []
        for work_order in work_orders:
            if work_order.state == "plan" or work_order.state == "ready" or work_order.state == "progress":
                json_content.extend(work_order.get_resources_default_import_array())
        now = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y%m%d_%H%M%S")
        return self.env['binary.download'].execute(
            base64.b64encode(json.dumps(json_content, indent=4)),
            "Import-WorkOrders-" + now + ".json"
        )
