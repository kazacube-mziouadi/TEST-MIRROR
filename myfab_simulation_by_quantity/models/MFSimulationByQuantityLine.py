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
    sequence = fields.Integer(string="Sequence", required=True, default=1)
    mf_simulation_id = fields.Many2one("mf.simulation.by.quantity", string="Simulation", ondelete="cascade")
    mf_selected_for_creation = fields.Boolean(string="Selected for creation", default=False)
    mf_quantity = fields.Float(string="Quantity", required=True, digits=dp.get_precision('Product quantity'))
    mf_product_id = fields.Many2one("product.product", string="Product", required=True)
    mf_bom_id = fields.Many2one("mrp.bom", string="Nomenclature", required=True)
    mf_routing_id = fields.Many2one("mrp.routing", string="Routing", required=True)
    mf_price_material = fields.Float(string="Material price", compute="_compute_mf_price_material", store=True,
                                     digits=dp.get_precision('Price technical'))
    mf_price_consumable = fields.Float(string="Consumable price", default=0.0, compute="_compute_mf_price_consumable",
                                       store=True, digits=dp.get_precision('Price technical'))
    mf_price_subcontracting = fields.Float(string="Subcontracting price", default=0.0,
                                           compute="_compute_mf_price_subcontracting", store=True,
                                           digits=dp.get_precision('Price technical'))
    mf_price_workforce = fields.Float(string="Workforce price", default=0.0,
                                      compute="_compute_mf_price_workforce", store=True,
                                      digits=dp.get_precision('Price technical'))
    mf_general_costs = fields.Float(string="General costs", default=0.0, digits=dp.get_precision('Price technical'))
    mf_unit_cost_price = fields.Float(string="Unit cost price", compute="_compute_unit_cost_price", store=True,
                                      default=0.0, digits=dp.get_precision('Price technical'))
    mf_unit_margin = fields.Float(string="Unit margin", help="Write an unit margin coefficient", default=0.0,
                                  digits=dp.get_precision('Price technical'))
    mf_unit_sale_price = fields.Float(string="Unit sale price", compute="_compute_unit_sale_price", store=True,
                                      default=0.0, digits=dp.get_precision('Price technical'))
    mf_hour_sale_price = fields.Float(string="Hour sale price", compute="_compute_hour_sale_price", store=True,
                                      default=0.0, digits=dp.get_precision('Price technical'))
    mf_total_cost_price = fields.Float(string="Total cost price", compute="_compute_total_cost_price", store=True,
                                       default=0.0, digits=dp.get_precision('Price technical'))
    mf_total_margin = fields.Float(string="Total margin", help="Write a total margin coefficient", default=0.0,
                                   digits=dp.get_precision('Price technical'))
    mf_total_sale_price = fields.Float(string="Total sale price", compute="_compute_total_sale_price", store=True,
                                       default=0.0, digits=dp.get_precision('Price technical'))

    @api.onchange("mf_product_id")
    def _onchange_mf_product_id(self):
        if not self.mf_product_id:
            self.mf_product_id = self.mf_simulation_id.mf_product_id
        if not self.mf_product_id or self.mf_bom_id.product_id != self.mf_product_id:
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

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_mf_price_material(self):
        self.mf_price_material, ptb, pucb, pc, pur1, puf1 = self.mf_bom_id.function_compute_price(
            button=False,
            type=self.mf_bom_id.type,
            product=self.mf_product_id,
            serie_eco=self.mf_quantity,
            prod_family=self.mf_bom_id.prod_family_id,
            return_detail_price=True,
            product_rc=self.mf_product_id,
            bom_rc=self.mf_bom_id
        )

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_mf_price_consumable(self):
        pm, ptb, pucb, self.mf_price_consumable, pur1, puf1 = self.mf_bom_id.function_compute_price(
            button=False,
            type=self.mf_bom_id.type,
            product=self.mf_product_id,
            serie_eco=self.mf_quantity,
            prod_family=self.mf_bom_id.prod_family_id,
            return_detail_price=True,
            product_rc=self.mf_product_id,
            bom_rc=self.mf_bom_id
        )

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_mf_price_subcontracting(self):
        self.mf_price_subcontracting = self.compute_price_for_resource_category(RESOURCE_CATEGORY_LABEL_SUBCONTRACTING)

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_mf_price_workforce(self):
        self.mf_price_workforce = self.compute_price_for_resource_category(RESOURCE_CATEGORY_LABEL_ROUTING_COST)

    def compute_price_for_resource_category(self, resource_category_name):
        total_routing_price_for_resource_category = 0.0
        for routing_line in self.mf_routing_id.routing_line_ids:
            total_routing_line_price_for_resource_category = 0.0
            for resource_category in routing_line.rl_resource_category_ids:
                if resource_category.category_id.name == resource_category_name:
                    total_resource_time = resource_category.preparation_time + resource_category.production_time_seizure
                    nb_resources = resource_category.nb_resource
                    hourly_rate = resource_category.category_id.hourly_rate
                    total_resource_category_price = total_resource_time * nb_resources * hourly_rate
                    total_routing_price_for_resource_category += total_resource_category_price
            total_routing_price_for_resource_category += total_routing_line_price_for_resource_category
        return total_routing_price_for_resource_category

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_unit_cost_price(self):
        self.mf_unit_cost_price = self.mf_price_material + self.mf_price_consumable + self.mf_price_subcontracting \
            + self.mf_price_workforce + self.mf_general_costs

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_unit_sale_price(self):
        self.mf_unit_sale_price = self.mf_unit_cost_price * self.mf_unit_margin

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_hour_sale_price(self):
        self.mf_hour_sale_price = self.mf_price_workforce * self.mf_unit_margin

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_total_cost_price(self):
        self.mf_total_cost_price = self.mf_unit_cost_price * self.mf_quantity

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_total_sale_price(self):
        self.mf_total_sale_price = self.mf_unit_sale_price * self.mf_quantity
