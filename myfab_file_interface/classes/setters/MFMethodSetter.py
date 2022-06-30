from openerp import models, fields, api, _


class MFMethodSetter(models.Model):
    _name = "mf.method.setter"
    _description = "myfab method setter"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Method name", required=True,
                       help="Name of the method to launch after export, at format method_name(param01, param02)")
    mf_model_dictionary_id = fields.Many2one(string="Model dictionary", required=False, ondelete="cascade")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def apply_method_on_record(self, record_id):
        self.env["mf.tools"].mf_launch_method_on_records(self.name, record_id)
