from openerp import models, fields, api, _, modules


class MFSimulationByQuantity(models.Model):
    _name = "mf.simulation.by.quantity"
    _description = "myfab Simulation by quantity"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, readonly=True)
    mf_customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    mf_product_id = fields.Many2one("product.product", string="Product", required=True)
    mf_bom_id = fields.Many2one("mrp.bom", string="Nomenclature", required=True)
    mf_routing_id = fields.Many2one("mrp.routing", string="Routing", required=True)
    mf_simulation_lines_ids = fields.One2many("mf.simulation.by.quantity.line", "mf_simulation_id", copy=True,
                                              string="Simulation lines")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.model
    def create(self, fields_list):
        # We write the simulation's name using it's sequence
        fields_list['name'] = self.env["ir.sequence"].get("mf.simulation.by.quantity")
        return super(MFSimulationByQuantity, self).create(fields_list)

    @api.onchange("mf_product_id")
    def onchange_mf_product_id(self):
        if self.mf_bom_id.product_id != self.mf_product_id:
            self.mf_bom_id = None
        if self.mf_bom_id not in self.mf_routing_id.bom_ids:
            self.mf_bom_id = None
