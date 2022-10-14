# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class MFWizardSimulationGenericCreation(models.TransientModel):
    _name = "mf.wizard.simulation.generic.creation"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    mf_model_to_create_id = fields.Many2one("ir.model", string="Model to create", readonly=True)
    mf_simulation_lines_ids = fields.Many2many("mf.simulation.by.quantity.line",
                                               "mf_wizard_simulation_generic_creation_lines_rel",
                                               "mf_wizard_simulation_generic_creation_id", "mf_simulation_line_id",
                                               copy=True, string="Exported simulation lines", readonly=True)

    # ===========================================================================
    # COLUMNS
    # ===========================================================================

    @api.model
    def default_get(self, fields_list):
        res = super(MFWizardSimulationGenericCreation, self).default_get(fields_list=fields_list)
        res["mf_model_to_create_id"] = self.env.context.get("mf_model_to_create_id")
        res["mf_simulation_lines_ids"] = self.env.context.get("mf_simulation_lines_ids")
        return res

    @api.one
    def action_multi_creation(self):
        return self.mf_simulation_lines_ids[0].mf_simulation_id.mf_action_multi_creation(self.mf_model_to_create_id, self.mf_simulation_lines_ids)

    @api.one
    def action_single_creation(self):
        return self.mf_simulation_lines_ids[0].mf_simulation_id.mf_action_single_creation(self.mf_model_to_create_id, self.mf_simulation_lines_ids)

