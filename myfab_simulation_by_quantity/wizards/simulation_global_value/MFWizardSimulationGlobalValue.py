# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
import datetime


class MFWizardSimulationGlobalValue(models.TransientModel):
    _name = "mf.wizard.simulation.global.value"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    mf_simulation_id = fields.Many2one("mf.simulation.by.quantity", string="Simulation to modify", readonly=1)

    mf_global_value_type = fields.Selection('_mf_type_get', string='Global value type', default=False)
    mf_global_value = fields.Float(string="Global value", help="Write the value to apply to all simulation lines", default=0.0, digits=dp.get_precision("Price technical"))

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.model
    def default_get(self, fields_list):
        res = super(MFWizardSimulationGlobalValue, self).default_get(fields_list=fields_list)
        res["mf_simulation_id"] = self.env.context.get("mf_simulation_id")
        return res

    @api.one
    def action_update_simulation(self):
        if self.mf_simulation_id and len(self.mf_global_value_type) > 1:
            for simulation_line_id in self.mf_simulation_id.mf_simulation_lines_ids:
                vals = {}
                vals[self.mf_global_value_type] = self.mf_global_value
                simulation_line_id.write(vals)

    def _get_editable_simulation_fields_names_list(self):
        model_id = self.env["ir.model"].search([("model", '=', "mf.simulation.by.quantity.line")], None, 1)
        editable_simulation_fields_ids = self.env["ir.model.fields"].search([
            ("name", "in", self.env["mf.simulation.by.quantity.line"].get_editable_simulation_fields_names_list()),
            ("model_id", '=', model_id.id)
        ])
        return editable_simulation_fields_ids

    def _get_global_value_editable_list(self):
        editable_fields_list = []
        for field_id in self._get_editable_simulation_fields_names_list():
            for field_config_id in self.mf_simulation_id.mf_field_configs_ids:
                if field_id.name == field_config_id.mf_field_id.name and field_config_id.mf_is_visible:
                    editable_fields_list.append((field_id.name, field_id.field_description))

        return editable_fields_list

    def _mf_type_get(self):
        print(self._get_global_value_editable_list())
        return self._get_global_value_editable_list()