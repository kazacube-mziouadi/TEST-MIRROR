from openerp import models, fields, api, _
from FilterInterfaceMF import FilterInterfaceMF


class FilterValueComparisonMF(models.Model, FilterInterfaceMF):
    _name = "filter.value.comparison.mf"
    _description = "myfab value comparison filter"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=False, help='')
    operator_mf = fields.Selection([
        ("=", "="), ("!=", "!="), ("<=", "<="), ("<", "<"), (">", ">"), (">=", ">="), ("=?", "=?"), ("=like", "=like"),
        ("=ilike", "=ilike"), ("like", "like"), ("not like", "not like"), ("ilike", "ilike"), ("not ilike", "not ilike"),
        ("in", "in"), ("not in", "not in"), ("child_of", "child_of"), ("parent_of", "parent_of"), ("~", "~")
    ], "Operator", required=True)
    value_mf = fields.Char(string="Value", required=True, help='')
    model_dictionary_field_mf = fields.Many2one(string="Model dictionary field", required=False, ondelete="cascade")

    def get_filter_tuple(self, field_name):
        return field_name, self.operator_mf, self.value_mf


