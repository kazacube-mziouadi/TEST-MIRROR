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
    mf_selectable_field_ids = fields.Many2one('mf.wizard.simulation.fields.list', string='Global value type', required=True, domain=lambda self: self._get_mf_domain())
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
            self._set_global_value_editable_list(simulation_id)
        return res

    @api.model
    def _get_mf_domain(self):
        return [("mf_simulation_id", "=", self.env.context.get("mf_simulation_id"))]

    def _set_global_value_editable_list(self, simulation_id):

        new_field_ids_list = []
        for field_id in self._get_editable_simulation_fields_names_list():
            for field_config_id in simulation_id.mf_field_configs_ids:
                if field_id.name == field_config_id.mf_field_id.name and field_config_id.mf_is_visible:
                    new_field_id = self.env["mf.wizard.simulation.fields.list"].create({
                        "name": field_id.field_description,
                        "mf_technical_name": field_id.name,
                        "mf_simulation_id": simulation_id.id,
                    })

                    new_field_ids_list.append(new_field_id.id)

        self.env["mf.wizard.simulation.fields.list"].search([
            ("mf_simulation_id", "=", simulation_id.id),
            ("id", "not in", new_field_ids_list)
        ]).unlink()

    def _get_editable_simulation_fields_names_list(self):
        model_id = self.env["ir.model"].search([("model", '=', "mf.simulation.by.quantity.line")], None, 1)
        editable_simulation_fields_ids = self.env["ir.model.fields"].search([
            ("name", "in", self.env["mf.simulation.by.quantity.line"].get_editable_simulation_fields_names_list()),
            ("model_id", '=', model_id.id)
        ])
        return editable_simulation_fields_ids

    @api.one
    def action_update_simulation(self):
        if self.mf_simulation_id and self.mf_selectable_field_ids:
            for simulation_line_id in self.mf_simulation_id.mf_simulation_lines_ids:
                vals = {}
                vals[self.mf_selectable_field_ids.mf_technical_name] = self.mf_global_value
                print(vals)
                #simulation_line_id.write(vals)

