from openerp import models, fields, api, _


class MFFieldSetter(models.Model):
    _name = "mf.field.setter"
    _description = "myfab field setter"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=False, help='')
    mf_field_to_set_id = fields.Many2one("ir.model.fields", string="Field to set", required=True,
                                         domain=lambda self: self._get_mf_field_to_set_id_domain())
    mf_value = fields.Char(string="Value to set", required=True, help="Value to set the field with at export.")
    mf_model_dictionary_id = fields.Many2one(string="Model dictionary", required=False, ondelete="cascade")

    @api.model
    def _get_mf_field_to_set_id_domain(self):
        if "model_to_export_id" in self.env.context:
            return [("model_id", "=", self.env.context["model_to_export_id"])]
        return []