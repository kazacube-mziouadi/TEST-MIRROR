from openerp import models, fields, api, _


class MFFieldSetter(models.Model):
    _name = "mf.field.setter"
    _description = "myfab field setter"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=False, help='')
    mf_field_to_set_id = fields.Many2one("ir.model.fields", string="Field to set", required=True)
    mf_value = fields.Char(string="Value to set", required=True, help="Value to set the field with at export.")
    mf_model_dictionary_id = fields.Many2one("file.interface.export.model.dictionary.mf",
                                             string="Model dictionary", required=False, ondelete="cascade")
    mf_model_dictionary_model_id_int = fields.Integer(compute="_compute_mf_model_dictionary_model_id_int")

    @api.one
    def _compute_mf_model_dictionary_model_id_int(self):
        print("***")
        self.mf_model_dictionary_model_id_id = 1
