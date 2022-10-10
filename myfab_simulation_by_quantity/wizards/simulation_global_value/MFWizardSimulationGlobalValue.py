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
    mf_simulation_id = fields.Many2one("mf.simulation.by.quantity", string="Simulation to modify", readonly=True)

    mf_selectable_field_ids = fields.Many2one('mf.wizard.simulation.fields.list', string='Global value type', required=True)
    mf_global_value = fields.Float(string="Global value", help="Write the value to apply to all simulation lines", default=0.0, digits=dp.get_precision("Price technical"))

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.model
    def default_get(self, fields_list):
        res = super(MFWizardSimulationGlobalValue, self).default_get(fields_list=fields_list)
        simulation_id = self.env["mf.simulation.by.quantity"].search([("id", '=', self.env.context.get("mf_simulation_id"))])
        
        if simulation_id:
            res["mf_simulation_id"] = simulation_id.id
            res["mf_selectable_field_ids"] = self._get_global_value_editable_list(simulation_id)
        return res

    @api.one
    def action_update_simulation(self):
        print(self.mf_selectable_field_ids)

        #if self.mf_simulation_id and len(self.mf_global_value_type) > 1:
            #for simulation_line_id in self.mf_simulation_id.mf_simulation_lines_ids:
                #vals = {}
                #vals[self.mf_global_value_type] = self.mf_global_value
                #simulation_line_id.write(vals)
            #self.mf_selectable_field_ids.unlink()

    def _get_global_value_editable_list(self, simulation_id):
        editable_fields_list = []
        editable_fields_list.append((5, 0, 0))
        for field_id in self._get_editable_simulation_fields_names_list():
            for field_config_id in simulation_id.mf_field_configs_ids:
                if field_id.name == field_config_id.mf_field_id.name and field_config_id.mf_is_visible:
                    wizard_simulation_field_id = self.env["mf.wizard.simulation.fields.list"].create({
                        "name": field_id.field_description,
                        "mf_technical_name": field_id.name,
                    })
                    editable_fields_list.append((0, 0, wizard_simulation_field_id.id))

        return editable_fields_list

    def _get_editable_simulation_fields_names_list(self):
        model_id = self.env["ir.model"].search([("model", '=', "mf.simulation.by.quantity.line")], None, 1)
        editable_simulation_fields_ids = self.env["ir.model.fields"].search([
            ("name", "in", self.env["mf.simulation.by.quantity.line"].get_editable_simulation_fields_names_list()),
            ("model_id", '=', model_id.id)
        ])
        return editable_simulation_fields_ids

