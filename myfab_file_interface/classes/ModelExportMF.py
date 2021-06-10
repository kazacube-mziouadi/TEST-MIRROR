from openerp import models, fields, api, _


class ModelExportMF(models.Model):
    _name = "model.export.mf"
    _description = "MyFab model export object"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=False, help='')
    model_to_export_mf = fields.Many2one("ir.model", string="Model to export")
    fields_to_export_mf = fields.Many2many("ir.model.fields", "model_export_mf_ir_model_fields_rel",
                                           "model_export_mf_id", "field_id", string="Fields to export", copy=False,
                                           readonly=False)