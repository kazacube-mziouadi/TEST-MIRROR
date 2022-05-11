from openerp import models, fields, api, _, modules
import openerp.addons.decimal_precision as dp

RESOURCE_CATEGORY_LABEL_SUBCONTRACTING = _("Subcontracting")
RESOURCE_CATEGORY_LABEL_ROUTING_COST = _("Routing cost")


class MFSimulationByQuantityLine(models.Model):
    _name = "mf.simulation.by.quantity.line"
    _description = "myfab Simulation by quantity line"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, readonly=True)
    mf_simulation_id = fields.Many2one("mf.simulation.by.quantity", string="Simulation", ondelete="cascade")
    mf_quantity = fields.Float(string="Quantity", required=True, digits=dp.get_precision('Product quantity'))
    mf_product_id = fields.Many2one("product.product", string="Product", required=True)
    mf_bom_id = fields.Many2one("mrp.bom", string="Nomenclature", required=True)
    mf_routing_id = fields.Many2one("mrp.routing", string="Routing", required=True)
    mf_price_material = fields.Float(string="Material price", default=0.0, digits=dp.get_precision('Price technical'))
    mf_price_consumable = fields.Float(string="Consumable price", default=0.0,
                                       digits=dp.get_precision('Price technical'))
    mf_price_subcontracting = fields.Float(string="Subcontracting price", default=0.0,
                                           digits=dp.get_precision('Price technical'))
    mf_price_workforce = fields.Float(string="Workforce price", default=0.0, digits=dp.get_precision('Price technical'))
    mf_general_costs = fields.Float(string="General costs", default=0.0, digits=dp.get_precision('Price technical'))
    mf_unit_cost_price = fields.Float(string="Unit cost price", default=0.0, digits=dp.get_precision('Price technical'))
    mf_unit_margin = fields.Float(string="Unit margin", help="Write an unit margin coefficient", default=0.0,
                                  digits=dp.get_precision('Price technical'))
    mf_unit_sale_price = fields.Float(string="Unit sale price", default=0.0, digits=dp.get_precision('Price technical'))
    mf_hour_sale_price = fields.Float(string="Hour sale price", default=0.0, digits=dp.get_precision('Price technical'))
    mf_total_cost_price = fields.Float(string="Total cost price", default=0.0,
                                       digits=dp.get_precision('Price technical'))
    mf_total_margin = fields.Float(string="Total margin", help="Write a total margin coefficient", default=0.0,
                                   digits=dp.get_precision('Price technical'))
    mf_total_sale_price = fields.Float(string="Total sale price", default=0.0,
                                       digits=dp.get_precision('Price technical'))

    @api.onchange("mf_quantity")
    def _onchange_simulation_line(self):
        self.mf_product_id = self.mf_simulation_id.mf_product_id if not self.mf_product_id else self.mf_product_id
        self.mf_bom_id = self.mf_simulation_id.mf_bom_id if not self.mf_bom_id else self.mf_bom_id
        self.mf_routing_id = self.mf_simulation_id.mf_routing_id if not self.mf_routing_id else self.mf_routing_id
        self.mf_price_material, ptb, pucb, self.mf_price_consumable, pur1, puf1 = self.mf_bom_id.function_compute_price(
            button=False,
            type=self.mf_bom_id.type,
            product=self.mf_product_id,
            serie_eco=self.mf_quantity,
            prod_family=self.mf_bom_id.prod_family_id,
            return_detail_price=True,
            product_rc=self.mf_product_id,
            bom_rc=self.mf_bom_id
        )
        self.mf_price_subcontracting, self.mf_price_workforce = self.compute_price_subcontracting()
        self.mf_unit_cost_price = self.compute_unit_cost_price()
        self.mf_unit_sale_price = self.compute_unit_sale_price()
        self.mf_hour_sale_price = self.compute_hour_sale_price()
        self.mf_total_cost_price = self.compute_total_cost_price()
        self.mf_total_sale_price = self.compute_total_sale_price()

    def compute_price_subcontracting(self):
        total_routing_price_subcontracting = 0.0
        total_routing_price_workforce = 0.0
        for routing_line in self.mf_routing_id.routing_line_ids:
            total_routing_line_price_subcontracting = 0.0
            total_routing_line_price_workforce = 0.0
            for resource_category in routing_line.rl_resource_category_ids:
                if resource_category.category_id.name in [
                    RESOURCE_CATEGORY_LABEL_SUBCONTRACTING, RESOURCE_CATEGORY_LABEL_ROUTING_COST
                ]:
                    total_resource_time = resource_category.preparation_time + resource_category.production_time_seizure
                    nb_resources = resource_category.nb_resource
                    hourly_rate = resource_category.category_id.hourly_rate
                    total_resource_category_price = total_resource_time * nb_resources * hourly_rate
                    if resource_category.category_id.name == RESOURCE_CATEGORY_LABEL_SUBCONTRACTING:
                        total_routing_line_price_subcontracting += total_resource_category_price
                    if resource_category.category_id.name == RESOURCE_CATEGORY_LABEL_ROUTING_COST:
                        total_routing_line_price_workforce += total_resource_category_price
            total_routing_price_subcontracting += total_routing_line_price_subcontracting
            total_routing_price_workforce += total_routing_line_price_workforce
        return total_routing_price_subcontracting, total_routing_price_workforce

    def compute_unit_cost_price(self):
        return self.mf_price_material + self.mf_price_consumable + self.mf_price_subcontracting \
               + self.mf_price_workforce + self.mf_general_costs

    def compute_unit_sale_price(self):
        return self.mf_unit_cost_price * self.mf_unit_margin

    def compute_hour_sale_price(self):
        return self.mf_price_workforce * self.mf_unit_margin

    def compute_total_cost_price(self):
        return self.mf_unit_cost_price * self.mf_quantity

    def compute_total_sale_price(self):
        return self.mf_unit_sale_price * self.mf_quantity
