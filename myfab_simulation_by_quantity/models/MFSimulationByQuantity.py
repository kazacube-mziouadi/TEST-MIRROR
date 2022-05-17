from openerp import models, fields, api, _, modules
from openerp.exceptions import MissingError


class MFSimulationByQuantity(models.Model):
    _name = "mf.simulation.by.quantity"
    _description = "myfab Simulation by quantity"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, readonly=True)
    mf_customer_id = fields.Many2one("res.partner", string="Customer")
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
        self.check_customer_and_lines_exist()
        sale_order_model_id = self.env["ir.model"].search([("model", '=', "sale.order")], None, 1)
        return self.open_model_creation_wizard(sale_order_model_id)

    @api.multi
    def create_quotation_button(self):
        self.check_customer_and_lines_exist()
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

    @api.multi
    def update_product_customer_info_button(self):
        self.check_customer_and_lines_exist()
        # One line case : no need to sort, we append directly the customer info and it's price within
        if len(self.mf_simulation_lines_ids) < 2:
            self.append_cinfo_line_to_product(
                self.mf_simulation_lines_ids[0].mf_product_id,
                self.mf_simulation_lines_ids[0].sequence,
                [self.get_product_price_creation_dict(self.mf_simulation_lines_ids[0])]
            )
            return
        # Multi lines case
        # We filter the simulation lines to keep only the selected ones
        simulation_lines_ids_sorted_list = filter(
            lambda simulation_line: simulation_line.mf_selected_for_creation,
            self.mf_simulation_lines_ids
        )
        # We sort the simulation lines list on the products' ids
        simulation_lines_ids_sorted_list = sorted(
            simulation_lines_ids_sorted_list,
            key=lambda simulation_line: simulation_line.mf_product_id.id
        )
        previous_simulation_line_id = None
        product_prices_list = []
        print(simulation_lines_ids_sorted_list)
        for index, simulation_line_id in enumerate(simulation_lines_ids_sorted_list):
            product_id = simulation_line_id.mf_product_id
            # If it's a product not processed yet, we create the product's customer info for the previous product
            if previous_simulation_line_id and previous_simulation_line_id.mf_product_id != product_id:
                self.append_cinfo_line_to_product(
                    previous_simulation_line_id.mf_product_id, previous_simulation_line_id.sequence, product_prices_list
                )
                product_prices_list = []
            # We append the prices of each line for the current product
            product_prices_list.append((0, 0, self.get_product_price_creation_dict(simulation_line_id)))
            # If it's the last line we create the product's customer info with the prices list within
            if index + 1 >= len(simulation_lines_ids_sorted_list):
                self.append_cinfo_line_to_product(
                    simulation_line_id.mf_product_id, simulation_line_id.sequence, product_prices_list
                )
            previous_simulation_line_id = simulation_line_id

    def append_cinfo_line_to_product(self, product_id, sequence, product_prices_list):
        for cinfo_id in product_id.cinfo_ids:
            if cinfo_id.partner_id == self.mf_customer_id:
                cinfo_id.unlink()
        product_id.cinfo_ids = [(0, 0, {
            "sequence": sequence,
            "partner_id": self.mf_customer_id.id,
            "state": "active",
            "currency_id": self.mf_customer_id.currency_id.id,
            "company_id": self.env.user.company_id.id,
            "uos_id": product_id.uos_id.id if product_id.uos_id else product_id.uom_id.id,
            "uos_category_id": product_id.uos_id.category_id.id if product_id.uos_id else product_id.uom_id.category_id.id,
            "uoi_id": product_id.sale_uoi_id.id if product_id.sale_uoi_id else product_id.uom_id.id,
            "uom_category_id": product_id.uom_id.category_id.id,
            "multiply_qty": 1.0,
            "pricelist_ids": product_prices_list
        })]

    @staticmethod
    def get_product_price_creation_dict(simulation_line_id):
        return {
            "min_qty": simulation_line_id.mf_quantity,
            "price": simulation_line_id.mf_total_sale_price,
        }

    def check_customer_and_lines_exist(self):
        if not self.mf_customer_id or not self.mf_simulation_lines_ids:
            raise MissingError(_(
                "Make sure a customer is selected and the simulation contains at least one line before using this button."
            ))

