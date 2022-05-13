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
    def default_get(self, fields_list):
        res = super(MFSimulationByQuantity, self).default_get(fields_list=fields_list)
        res["mf_product_id"] = self.env.context.get("mf_product_id")
        return res

    @api.model
    def create(self, fields_list):
        # We write the simulation's name using it's sequence
        fields_list['name'] = self.env["ir.sequence"].get("mf.simulation.by.quantity")
        return super(MFSimulationByQuantity, self).create(fields_list)

    @api.onchange("mf_product_id")
    def _onchange_mf_product_id(self):
        if not self.mf_product_id:
            if self.mf_bom_id:
                self.mf_bom_id = None
            return
        if self.mf_bom_id.product_id != self.mf_product_id:
            self.mf_bom_id = None
        if not self.mf_bom_id:
            product_bom_id = self.env["mrp.bom"].search([("product_id", '=', self.mf_product_id.id)], None, 1)
            if product_bom_id:
                self.mf_bom_id = product_bom_id.id

    @api.onchange("mf_bom_id")
    def _onchange_mf_bom_id(self):
        if not self.mf_bom_id:
            if self.mf_routing_id:
                self.mf_routing_id = None
            return
        if self.mf_bom_id not in self.mf_routing_id.bom_ids:
            self.mf_routing_id = None
        if not self.mf_routing_id:
            product_routing_id = self.env["mrp.routing"].search([("bom_ids", 'in', self.mf_bom_id.id)], None, 1)
            if product_routing_id:
                self.mf_routing_id = product_routing_id.id

    @api.multi
    def create_sale_order_button(self):
        sale_order_model_id = self.env["ir.model"].search([("model", '=', "sale.order")], None, 1)
        return self.open_model_creation_wizard(sale_order_model_id)

    @api.multi
    def create_quotation_button(self):
        quotation_model_id = self.env["ir.model"].search([("model", '=', "quotation")], None, 1)
        return self.open_model_creation_wizard(quotation_model_id)

    def open_model_creation_wizard(self, model_to_create_id):
        simulation_lines_to_create_ids = self.env["mf.simulation.by.quantity.line"].search([
            ("mf_simulation_id", '=', self.id), ("mf_selected_for_creation", '=', True)
        ])
        return {
            "name": _("Simulation by quantity - Model creation"),
            "view_mode": "form",
            "res_model": "mf.wizard.simulation.creation",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {
                "mf_model_to_create_id": model_to_create_id.id,
                "mf_simulation_lines_ids": [simulation_line.id for simulation_line in simulation_lines_to_create_ids]
            }
        }

    @api.multi
    def recompute_simulation_lines_button(self):
        for simulation_line_id in self.mf_simulation_lines_ids:
            simulation_line_id.mf_quantity = simulation_line_id.mf_quantity
