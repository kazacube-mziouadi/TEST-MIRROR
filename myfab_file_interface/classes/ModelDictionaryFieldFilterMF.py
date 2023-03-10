from openerp import models, fields, api, _


class ModelDictionaryFieldFilterMF(models.Model):
    _name = "model.dictionary.field.filter.mf"
    _description = "MyFab model dictionary link between a field and it's filters"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=False, help='')
    model_dictionary_mf = fields.Many2one(string="Model dictionary parent")
    field_to_export_mf = fields.Many2one("ir.model.fields", string="Field to filter", required=True,
                                         domain=lambda self: self._get_field_to_export_domain())
    value_comparisons_mf = fields.One2many("filter.value.comparison.mf", "model_dictionary_field_mf",
                                           string="Value compare filters", ondelete="cascade")
    datetime_delta_min_mf = fields.Many2one("filter.datetime.delta.mf",
                                            string="Datetime delta minimum filter")
    datetime_delta_max_mf = fields.Many2one("filter.datetime.delta.mf",
                                            string="Datetime delta maximum filter")
    hide_filters_view = fields.Boolean(compute='compute_hide_filters_view', default=True)
    hide_filters_datetime_view = fields.Boolean(compute='compute_hide_filters_datetime_view')
    number_of_filters_on_field = fields.Integer(compute='compute_number_of_filters_on_field',
                                                string="Number of filters on field", readonly=True)

    @api.model
    def _get_field_to_export_domain(self):
        if "model_to_filter_id" in self.env.context:
            model_to_filter_id = self.env.context["model_to_filter_id"]
            model = self.env["ir.model"].search([("id", "=", model_to_filter_id)], None, 1)
            return [("id", "in", [field.id for field in model.field_id])]
        return []

    @api.one
    @api.depends("field_to_export_mf")
    def compute_hide_filters_view(self):
        self.hide_filters_view = (not self.field_to_export_mf)

    @api.one
    @api.depends("field_to_export_mf")
    def compute_hide_filters_datetime_view(self):
        self.hide_filters_datetime_view = (not self.field_to_export_mf.ttype == "datetime")

    @api.one
    @api.depends("value_comparisons_mf", "datetime_delta_min_mf", "datetime_delta_max_mf")
    def compute_number_of_filters_on_field(self):
        self.number_of_filters_on_field = len(self.value_comparisons_mf)
        if self.field_to_export_mf.ttype in ["datetime", "date"]:
            if self.datetime_delta_min_mf:
                self.number_of_filters_on_field += 1
            if self.datetime_delta_max_mf:
                self.number_of_filters_on_field += 1

    def get_field_filters_list_to_apply(self):
        field_name = self.field_to_export_mf.name
        filters_list = []
        if self.field_to_export_mf.ttype in ["datetime", "date"]:
            if self.datetime_delta_min_mf:
                filters_list.append(self.datetime_delta_min_mf.get_filter_tuple(field_name, '>='))
            if self.datetime_delta_max_mf:
                filters_list.append(self.datetime_delta_max_mf.get_filter_tuple(field_name, '<='))
        for value_comparison in self.value_comparisons_mf:
            filters_list.append(value_comparison.get_filter_tuple(field_name))
        return filters_list


