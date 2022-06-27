from openerp import models, fields, api, _


class ModelDictionaryFieldFilterMF(models.Model):
    _name = "model.dictionary.field.filter.mf"
    _description = "myfab model dictionary link between a field and it's filters"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=False)
    model_dictionary_mf = fields.Many2one(string="Model dictionary parent", ondelete="cascade")
    field_to_export_mf = fields.Many2one("ir.model.fields", string="Field to filter", required=True,
                                         domain=lambda self: self._get_field_to_export_domain())
    value_comparisons_mf = fields.One2many("filter.value.comparison.mf", "model_dictionary_field_mf",
                                           string="Value compare filters")
    datetime_delta_min_mf = fields.Many2one("filter.datetime.delta.mf", string="Datetime delta minimum filter")
    datetime_delta_max_mf = fields.Many2one("filter.datetime.delta.mf", string="Datetime delta maximum filter")
    hide_filters_view = fields.Boolean(compute="compute_hide_filters_view", default=True)
    mf_hide_child_model_field_filters_view = fields.Boolean(compute="compute_mf_hide_child_model_field_filters_view",
                                                            default=True)
    hide_filters_datetime_view = fields.Boolean(compute="compute_hide_filters_datetime_view")
    number_of_filters_on_field = fields.Integer(compute="compute_number_of_filters_on_field",
                                                string="Number of filters on field", readonly=True)
    mf_child_model_fields_filters = fields.One2many("model.dictionary.field.filter.mf", "model_dictionary_mf",
                                                    copy=True, string="Child model's fields filters")
    mf_field_relation_model_id = fields.Many2one("ir.model", string="Field's relation model",
                                                 compute="compute_mf_field_relation_model_id")

    # ===========================================================================
    # METHODS - DOMAIN
    # ===========================================================================

    @api.model
    def _get_field_to_export_domain(self):
        if "model_to_filter_id" in self.env.context:
            return [("model_id", "=", self.env.context["model_to_filter_id"])]
        return []

    # ===========================================================================
    # METHODS - COMPUTE
    # ===========================================================================

    @api.one
    @api.depends("field_to_export_mf")
    def compute_hide_filters_view(self):
        self.hide_filters_view = not self.field_to_export_mf or self.field_to_export_mf.relation

    @api.one
    @api.depends("field_to_export_mf")
    def compute_mf_hide_child_model_field_filters_view(self):
        self.mf_hide_child_model_field_filters_view = not self.field_to_export_mf or not self.field_to_export_mf.relation

    @api.one
    @api.depends("field_to_export_mf")
    def compute_hide_filters_datetime_view(self):
        self.hide_filters_datetime_view = self.field_to_export_mf.ttype not in ["date", "datetime"]

    @api.one
    @api.depends("value_comparisons_mf", "datetime_delta_min_mf", "datetime_delta_max_mf")
    def compute_number_of_filters_on_field(self):
        self.number_of_filters_on_field = len(self.value_comparisons_mf)
        if self.field_to_export_mf.ttype in ["datetime", "date"]:
            if self.datetime_delta_min_mf:
                self.number_of_filters_on_field += 1
            if self.datetime_delta_max_mf:
                self.number_of_filters_on_field += 1

    @api.one
    @api.depends("field_to_export_mf")
    def compute_mf_field_relation_model_id(self):
        if self.field_to_export_mf.relation:
            self.mf_field_relation_model_id = self.env["ir.model"].search([
                ("model", '=', self.field_to_export_mf.relation)
            ])

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def get_field_filters_list_to_apply(self):
        field_name = self.field_to_export_mf.name
        filters_list = []
        # Relational field case
        if self.field_to_export_mf.relation:
            for child_model_fields_filter in self.mf_child_model_fields_filters:
                filtered_children_records_ids = self.env[self.field_to_export_mf.relation].search(
                    child_model_fields_filter.get_field_filters_list_to_apply()
                )
                filtered_children_records_ids_ids = map(
                    lambda child_record_id: child_record_id.id, filtered_children_records_ids
                )
                filters_list.append((self.field_to_export_mf.name, "in", filtered_children_records_ids_ids))
            return filters_list
        # Datetime field's comparison case
        if self.field_to_export_mf.ttype in ["datetime", "date"]:
            if self.datetime_delta_min_mf:
                filters_list.append(self.datetime_delta_min_mf.get_filter_tuple(field_name, '>='))
            if self.datetime_delta_max_mf:
                filters_list.append(self.datetime_delta_max_mf.get_filter_tuple(field_name, '<='))
        # Classic fields' comparisons
        for value_comparison in self.value_comparisons_mf:
            filters_list.append(value_comparison.get_filter_tuple(field_name))
        return filters_list


