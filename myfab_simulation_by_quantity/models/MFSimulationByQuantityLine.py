from openerp import models, fields, api, _, modules


class MFSimulationByQuantityLine(models.Model):
    _name = "mf.simulation.by.quantity.line"
    _description = "myfab Simulation by quantity line"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, readonly=True)
    mf_simulation_id = fields.Many2one("mf.simulation.by.quantity", string="Simulation", required=True)
