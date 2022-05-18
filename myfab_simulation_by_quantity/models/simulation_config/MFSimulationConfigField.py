from openerp import models, fields, api, _, modules


class MFSimulationConfigField(models.Model):
    _name = "mf.simulation.config.field"
    _description = "myfab Simulation by quantity"

    # ===========================================================================
    # COLUMNS - A simulation config field can be linked to a config OR a simulation
    # ===========================================================================
    name = fields.Char(string="Name", size=64, readonly=True)
    mf_simulation_config_id = fields.Many2one("mf.simulation.config", string="Simulation config")
    mf_simulation_id = fields.Many2one("mf.simulation.by.quantity", string="Simulation")
    mf_is_visible = fields.Boolean(string="Is visible", default=True)
    mf_field_id = fields.Many2one("ir.model.fields", string="Configured field")

    # ===========================================================================
    # METHODS
    # ===========================================================================
