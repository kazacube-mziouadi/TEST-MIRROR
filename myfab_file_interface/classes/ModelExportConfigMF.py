from openerp import models, fields, api, _


class ModelExportConfigMF(models.Model):
    _name = "model.export.config.mf"
    _description = "MyFab model export config"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=False, help='')
    model_to_export_mf = fields.Many2one("ir.model", string="Model to Export")
    fields_to_export_mf = fields.Many2many("ir.model.fields", "model_export_config_mf_ir_model_fields_rel",
                                           "model_export_config_mf_id", "field_id", string="Fields to export", copy=False,
                                           readonly=False)
    parent_model_export_config_mf = fields.Many2one("model.export.config.mf", string="Parent MyFab Model Export Config",
                                                    readonly=True)
    children_model_export_configs_mf = fields.One2many("model.export.config.mf", "parent_model_export_config_mf",
                                                       string="Children MyFab Model Export Config", ondelete="cascade")
    hide_fields_view = fields.Boolean(compute='_compute_hide_fields_view')

    @api.onchange("fields_to_export_mf")
    def _onchange_sub_fields_to_export_mf(self):
        print("ON CHANGE")
        for field_to_export in self.fields_to_export_mf:
            if field_to_export.ttype in ["many2many", "one2many", "many2one"]:
                sub_model_to_export = self.env["ir.model"].search([("model", '=', field_to_export.relation)], None, 1)
                if not self.is_sub_model_in_children_model_export_config(sub_model_to_export):
                    # If we modify the "self" element through an onchange, we have to use "update" (not "write")
                    self.update({
                        "children_model_export_configs_mf": [(0, _, {
                            "model_to_export_mf": sub_model_to_export.id,
                            "parent_model_export_config_mf": self._origin.id
                        })]
                    })

    def is_sub_model_in_children_model_export_config(self, sub_model):
        for child_model_export_config in self.children_model_export_configs_mf:
            if child_model_export_config.model_to_export_mf.id == sub_model.id:
                return True
        return False

    @api.one
    @api.depends('model_to_export_mf')
    def _compute_hide_fields_view(self):
        print(self.id)
        print(self.model_to_export_mf)
        print(not self.id or not self.model_to_export_mf)
        self.hide_fields_view = (not self.id or not self.model_to_export_mf)

    def get_dict_of_objects_to_export(self, model_to_export_config):
        list_of_objects_to_export = {}
        objects_to_export = self.env[model_to_export_config.model_to_export_mf.model].search([])
        for object_to_export in objects_to_export:
            list_of_objects_to_export[object_to_export.display_name] = self.get_dict_of_object_to_export(
                object_to_export
            )
        return list_of_objects_to_export

    def get_dict_of_object_to_export(self, object_to_export):
        object_dict = {}
        for field_to_export in self.fields_to_export_mf:
            object_field_value = getattr(object_to_export, field_to_export.name)
            if field_to_export.ttype in ["many2many", "one2many"]:
                # List of objects
                sub_objects_dict = {}
                child_model_export_config = self.get_child_model_export_config_for_field(field_to_export)
                for sub_object in object_field_value:
                    sub_objects_dict[sub_object.display_name] = child_model_export_config.get_dict_of_object_to_export(
                        sub_object
                    )
                object_dict[field_to_export.name] = sub_objects_dict
            elif field_to_export.ttype == "many2one":
                # Object
                child_model_export_config = self.get_child_model_export_config_for_field(field_to_export)
                object_dict[field_to_export.name] = child_model_export_config.get_dict_of_object_to_export(
                    object_field_value
                )
            else:
                # String
                object_dict[field_to_export.name] = object_field_value
        return object_dict

    def get_child_model_export_config_for_field(self, field_to_export):
        return self.children_model_export_configs_mf.search(
            [("model_to_export_mf", "=", field_to_export.relation)], None, 1
        )
