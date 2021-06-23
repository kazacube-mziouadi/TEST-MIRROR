from openerp import models, fields, api, _


class ModelDictionaryMF(models.AbstractModel):
    _name = "model.dictionary.mf"
    _auto = False
    _description = "MyFab model dictionary abstract generator - to use it, you have to inherit from this model, " \
                   "override it's Many2many and One2many fields, add a Many2one to target the model where it is used."

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=False, help='')
    model_to_export_mf = fields.Many2one("ir.model", string="Model to Export")
    fields_to_export_mf = fields.Many2many("ir.model.fields", "model_export_config_mf_ir_model_fields_rel",
                                           "model_export_config_mf_id", "model_field_id", string="Fields to export",
                                           copy=False, readonly=False)
    fields_filters_mf = fields.One2many("model.dictionary.field.filter.mf", "model_dictionary_mf",
                                        string="Filters to apply on fields", ondelete="cascade")
    parent_model_dictionary_mf = fields.Many2one(string="Parent MyFab Model Export Config")
    children_model_dictionaries_mf = fields.One2many("model.dictionary.mf", "parent_model_dictionary_mf",
                                                     string="Children MyFab Model Export Config", ondelete="cascade")
    hide_fields_view = fields.Boolean(compute='compute_hide_fields_view')
    hide_filters_view = fields.Boolean(compute='compute_hide_filters_view')

    @api.onchange("fields_to_export_mf")
    def onchange_sub_fields_to_export_mf(self):
        # To enrich the children model exports list automatically
        for field_to_export in self.fields_to_export_mf:
            if field_to_export.ttype in ["many2many", "one2many", "many2one"]:
                sub_model_to_export = self.env["ir.model"].search([("model", '=', field_to_export.relation)], None, 1)
                if not self.is_sub_model_in_children_model_export_config(sub_model_to_export):
                    # We retrieve the currently selected elements
                    children_model_export_configs_array = [child.id for child in self.children_model_dictionaries_mf]
                    # We add the new element
                    children_model_export_configs_array.append({
                        "model_to_export_mf": sub_model_to_export.id
                    })
                    # To modify the temporary many2many list shown on screen, we have to use "update" (not "write")
                    self.update({
                        "children_model_dictionaries_mf": children_model_export_configs_array
                    })

    def is_sub_model_in_children_model_export_config(self, sub_model):
        for child_model_export_config in self.children_model_dictionaries_mf:
            if child_model_export_config.model_to_export_mf.id == sub_model.id:
                return True
        return False

    @api.one
    @api.depends('model_to_export_mf')
    def compute_hide_fields_view(self):
        self.hide_fields_view = (not self.id or not self.model_to_export_mf)

    @api.one
    @api.depends('fields_filters_mf')
    def compute_hide_filters_view(self):
        self.hide_filters_view = (not self.fields_to_export_mf)

    def get_dict_of_objects_to_export(self, model_to_export_dict):
        list_of_objects_to_export = {}
        objects_to_export = self.env[model_to_export_dict.model_to_export_mf.model].search([])
        for object_to_export in objects_to_export:
            list_of_objects_to_export[object_to_export.display_name] = self.get_dict_of_object_to_export(
                object_to_export
            )
        return list_of_objects_to_export

    def get_dict_of_object_to_export(self, object_to_export):
        object_dict = {}
        for field_to_export in self.fields_to_export_mf:
            object_dict[field_to_export.name] = self.get_value_of_field_to_export(field_to_export, object_to_export)
        return object_dict

    def get_value_of_field_to_export(self, field_to_export, object_to_export):
        object_field_value = getattr(object_to_export, field_to_export.name)
        if field_to_export.ttype in ["many2many", "one2many"]:
            # List of objects
            sub_objects_dict = {}
            child_model_export_config = self.get_child_model_export_config_for_field(field_to_export)
            for sub_object in object_field_value:
                sub_objects_dict[sub_object.display_name] = child_model_export_config.get_dict_of_object_to_export(
                    sub_object
                )
            return sub_objects_dict
        elif field_to_export.ttype == "many2one":
            # Object
            child_model_export_config = self.get_child_model_export_config_for_field(field_to_export)
            return child_model_export_config.get_dict_of_object_to_export(
                object_field_value
            )
        else:
            # String
            return object_field_value

    def get_child_model_export_config_for_field(self, field_to_export):
        for child_model_dictionary in self.children_model_dictionaries_mf:
            if child_model_dictionary.model_to_export_mf.model == field_to_export.relation:
                return child_model_dictionary
        return None
