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
    children_model_export_configs = fields.One2many("model.export.config.mf", "parent_model_export_config_mf",
                                                    string="Children MyFab Model Export Config", ondelete="cascade")
    hide_fields_view = fields.Boolean(compute='_compute_hide_fields_view')

    @api.onchange("fields_to_export_mf")
    def _onchange_sub_fields_to_export_mf(self):
        print("ON CHANGE")
        for field_to_export in self.fields_to_export_mf:
            if field_to_export.ttype in ["many2many", "one2many", "many2one"]:
                sub_model_to_export = self.env["ir.model"].search([("model", '=', field_to_export.relation)], None, 1)
                if not self.is_sub_model_in_children_model_export_config(sub_model_to_export):
                    print(self._origin)
                    self.env["model.export.config.mf"].create({
                        "model_to_export_mf": sub_model_to_export.id,
                        "parent_model_export_config_mf": self._origin.id
                    })
                    self.update({
                        "children_model_export_configs": [(0, 0, {
                            "model_to_export_mf": sub_model_to_export.id,
                            "parent_model_export_config_mf": self._origin.id
                        })]
                    })

    def is_sub_model_in_children_model_export_config(self, sub_model):
        for child_model_export_config in self.children_model_export_configs:
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
