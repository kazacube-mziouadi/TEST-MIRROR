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
    mf_selectable_field_ids = fields.Many2one('mf.wizard.simulation.fields.list', string='Global value type', required=True, domain=lambda self: self._get_mf_domain(), ondelete="cascade")
    mf_global_value = fields.Float(string="Global value", help="Write the value to apply to all simulation lines", default=0.0, digits=dp.get_precision("Price technical"))

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.model
    def default_get(self, fields_list):
        res = super(MFWizardSimulationGlobalValue, self).default_get(fields_list=fields_list)
        res["mf_simulation_id"] = self.env.context.get("mf_simulation_id")
        res["mf_selectable_field_ids"] = self.env.context.get("mf_selectable_field_ids")
        return res

    @api.model
    def _get_mf_domain(self):
        return [("mf_simulation_id", "=", self.env.context.get("mf_simulation_id"))]
    
    @api.one
    def action_update_simulation(self):
        if self.mf_simulation_id and self.mf_selectable_field_ids:
            for simulation_line_id in self.mf_simulation_id.mf_simulation_lines_ids:
                vals = {}
                vals[self.mf_selectable_field_ids.mf_technical_name] = self.mf_global_value
                simulation_line_id.write(vals)

