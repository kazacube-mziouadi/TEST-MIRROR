from openerp import models, fields, api, _
import json
import os


class MyFabFileInterfaceImportMF(models.Model):
    _name = "myfab.file.interface.import.mf"
    _description = "MyFab file interface import configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=True, help='')
    import_directory_path_mf = fields.Char(string="Files path", default="/etc/openprod_home/MyFabFileInterface/Imports/WorkOrders")
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
        files = [f for f in os.listdir(self.import_directory_path_mf) if os.path.isfile(os.path.join(self.import_directory_path_mf, f))]
        for file_name in files:
            self.import_file(file_name)
            self.archive_file(file_name)

    def import_file(self, file_name):
        file = open(os.path.join(self.import_directory_path_mf, file_name), "r")
        file_content = file.read()
        self.last_json_imported_mf = file_content
        objects_to_create_array = json.loads(file_content)
        for object_to_create_dictionary in objects_to_create_array:
            model_returned = self.apply_orm_method_to_model(
                object_to_create_dictionary["model"],
                object_to_create_dictionary["fields"],
                object_to_create_dictionary["write"] if "write" in object_to_create_dictionary else False,
                object_to_create_dictionary["method"]
            )
            if "callback" in object_to_create_dictionary:
                callback_method_on_model = getattr(model_returned, object_to_create_dictionary["callback"])
                callback_method_on_model()

    def apply_orm_method_to_model(self, model_name, model_fields, model_fields_to_write, orm_method_name):
        # Retrieving the ID of each field which is an object recursively
        self.set_fields_object_to_ids_in_dict(model_fields, model_name)
        if model_fields_to_write:
            self.set_fields_object_to_ids_in_dict(model_fields_to_write, model_name)
        if orm_method_name == "create":
            model_fields["user_id"] = self.env.user.id
            return self.env[model_name].create(model_fields)
        elif orm_method_name in ["search", "write"]:
            # "Search" ORM method takes an array of tuples
            model_fields = [(key, '=', value) for key, value in model_fields.items()]
            model_found = self.env[model_name].search(model_fields, None, 1)
            if orm_method_name == "search":
                return model_found
            orm_method_on_model = getattr(model_found, orm_method_name)
            if model_fields_to_write:
                orm_method_on_model(model_fields_to_write)
            else:
                orm_method_on_model()
            return model_found

    def set_fields_object_to_ids_in_dict(self, fields_dict, model_name):
        for field_name in fields_dict:
            if type(fields_dict[field_name]) is dict:
                fields_dict[field_name] = self.get_field_object_id(
                    model_name,
                    field_name,
                    fields_dict[field_name]
                )

    def get_field_object_id(self, parent_model_name, field_name, field_object_dictionary):
        parent_model = self.env["ir.model"].search([
            ("model", '=', parent_model_name)
        ], None, 1)
        field_model = self.env["ir.model.fields"].search([
            ("name", '=', field_name),
            ("model_id", '=', parent_model.id)
        ], None, 1)
        for sub_field_name in field_object_dictionary:
            if type(field_object_dictionary[sub_field_name]) is dict:
                field_object_dictionary[sub_field_name] = self.get_field_object_id(
                    field_model.relation,
                    sub_field_name,
                    field_object_dictionary[sub_field_name]
                )
        field_object_dictionary_tuples = [(key, '=', value) for key, value in field_object_dictionary.items()]
        field_object = self.env[field_model.relation].search(field_object_dictionary_tuples, None, 1)
        return field_object.id

    def archive_file(self, file_name):
        archive_path = os.path.join(self.import_directory_path_mf, "Archives")
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
