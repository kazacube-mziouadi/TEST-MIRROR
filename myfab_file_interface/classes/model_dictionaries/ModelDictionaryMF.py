from openerp import models, fields, api, _
from openerp.exceptions import MissingError


class ModelDictionaryMF(models.AbstractModel):
    _name = "model.dictionary.mf"
    _auto = False
    _description = "myfab model dictionary abstract generator - to use it, you have to inherit from this model, " \
                   "override it's Many2many and One2many fields, add a Many2one to target the model where it is used."

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=False, help='')
    model_to_export_mf = fields.Many2one("ir.model", string="Model to Export")
    fields_to_export_mf = fields.Many2many("ir.model.fields", "model_dictionary_mf_ir_model_fields_rel",
                                           "model_dictionary_mf_id", "model_field_id", string="Fields to export",
                                           copy=True, readonly=False)
    fields_filters_mf = fields.One2many("model.dictionary.field.filter.mf", "model_dictionary_mf", copy=True,
                                        string="Filters to apply on fields at export")
    parent_model_dictionary_mf = fields.Many2one(string="Parent myfab model export config", ondelete="cascade")
    children_model_dictionaries_mf = fields.One2many("model.dictionary.mf", "parent_model_dictionary_mf", copy=True,
                                                     string="Children myfab model export configs")
    hide_fields_view = fields.Boolean(compute="compute_hide_fields_view")
    number_of_records_exported = fields.Integer(string="Number of records exported", readonly=True)
    number_of_records_to_export_limit_mf = fields.Integer(string="Number of records to export limit",
                                                          help="If set to 0, no limit is applied.", default=None)
    mf_fields_to_search = fields.Many2many("ir.model.fields", "model_dictionary_mf_fields_to_search_rel",
                                           "model_dictionary_mf_id", "model_field_id",
                                           string="Fields to search at import", copy=True, readonly=False,
                                           help="At import, fields on which search the records to process. \
                                                Warning : if no field is set here, all the records will be processed.")
    mf_field_setters = fields.One2many("mf.field.setter", "mf_model_dictionary_id", copy=True,
                                       string="Fields setting at export")

    # ===========================================================================
    # METHODS - FIELDS
    # ===========================================================================

    # To enrich the children model exports list automatically
    @api.onchange("fields_to_export_mf")
    def onchange_sub_fields_to_export_mf(self):
        for field_to_export in self.fields_to_export_mf:
            if field_to_export.ttype in ["many2many", "one2many", "many2one"]:
                sub_model_to_export = self.env["ir.model"].search([("model", '=', field_to_export.relation)], None, 1)
                if not self.is_sub_model_in_children_model_dictionary(sub_model_to_export):
                    # We retrieve the currently selected elements
                    children_model_dictionaries_list = [child.id for child in self.children_model_dictionaries_mf]
                    # We add the new element
                    children_model_dictionaries_list.append({
                        "model_to_export_mf": sub_model_to_export.id
                    })
                    # To modify the temporary many2many list shown on screen, we have to use "update" (not "write")
                    self.update({
                        "children_model_dictionaries_mf": children_model_dictionaries_list
                    })

    def is_sub_model_in_children_model_dictionary(self, sub_model):
        for child_model_dictionary in self.children_model_dictionaries_mf:
            if child_model_dictionary.model_to_export_mf.id == sub_model.id:
                return True
        return False

    @api.one
    @api.depends('model_to_export_mf')
    def compute_hide_fields_view(self):
        self.hide_fields_view = not self.id or not self.model_to_export_mf

    # ===========================================================================
    # METHODS - EXPORT
    # ===========================================================================
    def get_list_of_records_to_export(self, ids_to_search_list=False):
        list_of_records_to_export = []
        filters_list = self.get_filters_list_to_apply()
        if ids_to_search_list:
            filters_list.append(("id", "in", ids_to_search_list))
        objects_to_export = self.env[self.model_to_export_mf.model].search(
            filters_list, limit=self.number_of_records_to_export_limit_mf
        )
        self.number_of_records_exported = len(objects_to_export)
        for object_to_export in objects_to_export:
            list_of_records_to_export.append(self.get_dict_of_record_to_export(object_to_export))
            object_to_export.write(self.get_dict_of_values_to_set_at_export())
        return list_of_records_to_export

    def get_filters_list_to_apply(self):
        filters_list = []
        for field_filter in self.fields_filters_mf:
            filters_list = filters_list + field_filter.get_field_filters_list_to_apply()
        return filters_list

    def get_dict_of_record_to_export(self, object_to_export, apply_filters=False):
        if apply_filters:
            orm_filtered_search_result = self.env[self.model_to_export_mf.model].search(
                self.get_filters_list_to_apply() + [("id", "=", object_to_export.id)]
            )
            if not orm_filtered_search_result:
                return {}
        object_dict = {}
        for field_to_export in self.fields_to_export_mf:
            object_dict[field_to_export.name] = self.get_value_of_field_to_export(field_to_export, object_to_export)
        return object_dict

    def get_value_of_field_to_export(self, field_to_export, object_to_export):
        object_field_value = getattr(object_to_export, field_to_export.name)
        if field_to_export.ttype in ["many2many", "one2many"]:
            # List of records
            child_model_dictionary = self.get_child_model_dictionary_for_field(field_to_export)
            return child_model_dictionary.get_list_of_records_to_export(
                [sub_object.id for sub_object in object_field_value] if object_field_value else []
            )
        elif field_to_export.ttype == "many2one":
            # Record
            child_model_dictionary = self.get_child_model_dictionary_for_field(field_to_export)
            return child_model_dictionary.get_dict_of_record_to_export(object_field_value, apply_filters=True)
        else:
            # String, boolean, integer...
            return "" if object_field_value is False and field_to_export.ttype != "boolean" else object_field_value

    def get_child_model_dictionary_for_field(self, field_to_export, raise_error_if_not_found=True):
        for child_model_dictionary in self.children_model_dictionaries_mf:
            if child_model_dictionary.model_to_export_mf.model == field_to_export.relation:
                return child_model_dictionary
        if raise_error_if_not_found:
            raise MissingError("No model dictionary found for model " + field_to_export.relation)
        else:
            return False

    def get_fields_names_list(self, prefix=""):
        fields_names_list = []
        for field_to_export in self.fields_to_export_mf:
            if field_to_export.relation:
                child_model_dictionary = self.get_child_model_dictionary_for_field(field_to_export)
                child_prefix = prefix + field_to_export.name + '/' if prefix else field_to_export.name + '/'
                fields_names_list = fields_names_list + child_model_dictionary.get_fields_names_list(child_prefix)
            else:
                fields_names_list.append(prefix + field_to_export.name)
        return fields_names_list

    def get_dict_of_values_to_set_at_export(self):
        return {field_setter.mf_field_to_set_id.name: field_setter.mf_value for field_setter in self.mf_field_setters}
