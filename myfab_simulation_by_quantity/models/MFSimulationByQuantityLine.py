from openerp import models, fields, api, _, modules


class MFSimulationByQuantityLine(models.Model):
    _name = "mf.simulation.by.quantity.line"
    _description = "myfab Simulation by quantity line"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, readonly=True)
    mf_simulation_id = fields.Many2one("mf.simulation.by.quantity", string="Simulation", required=True)
    mf_quantity = fields.Float(string="Quantity")
    mf_price_material = fields.Float(string="Material price")
    mf_price_consumable = fields.Float(string="Consumable price")
    mf_price_subcontracting = fields.Float(string="Subcontracting price")
    mf_price_workforce = fields.Float(string="Workforce price")
    mf_general_costs = fields.Float(string="General costs")