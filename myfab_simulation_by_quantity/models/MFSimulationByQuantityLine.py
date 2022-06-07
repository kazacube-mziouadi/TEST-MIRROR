from openerp import models, fields, api, _, modules
import openerp.addons.decimal_precision as dp
from openerp.exceptions import MissingError

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
    mf_selected_for_creation = fields.Boolean(string="Selected for creation", default=True)
    mf_quantity = fields.Float(string="Quantity", required=True, digits=dp.get_precision('Product quantity'))
    mf_product_id = fields.Many2one("product.product", string="Product", required=True)
    mf_bom_id = fields.Many2one("mrp.bom", string="Nomenclature", required=True)
    mf_routing_id = fields.Many2one("mrp.routing", string="Routing", required=True)
    mf_price_material = fields.Float(string="Material price", compute="_compute_mf_price_material_and_consumable",
                                     store=True, digits=dp.get_precision("Price technical"))
    mf_price_consumable_is_visible = fields.Boolean(string="Consumable price is visible",
                                                    compute="_compute_mf_price_consumable_is_visible")
    mf_price_consumable = fields.Float(string="Consumable price", default=0.0,
                                       compute="_compute_mf_price_material_and_consumable",
                                       store=True, digits=dp.get_precision("Price technical"))
    mf_price_subcontracting_is_visible = fields.Boolean(string="Subcontracting price is visible",
                                                        compute="_compute_mf_price_subcontracting_is_visible")
    mf_price_subcontracting = fields.Float(string="Subcontracting price", default=0.0,
                                           compute="_compute_mf_price_subcontracting", store=True,
                                           digits=dp.get_precision("Price technical"))
    mf_price_workforce_is_visible = fields.Boolean(string="Workforce price is visible",
                                                   compute="_compute_mf_price_workforce_is_visible")
    mf_price_workforce = fields.Float(string="Workforce price", default=0.0,
                                      compute="_compute_mf_price_workforce", store=True,
                                      digits=dp.get_precision("Price technical"))
    mf_general_costs_is_visible = fields.Boolean(string="General costs is visible",
                                                 compute="_compute_mf_general_costs_is_visible")
    mf_general_costs = fields.Float(string="General costs", default=0.0, digits=dp.get_precision("Price technical"))
    mf_unit_cost_price = fields.Float(string="Unit cost price", compute="_compute_unit_cost_price", store=True,
                                      default=0.0, digits=dp.get_precision("Price technical"))
    mf_unit_margin_is_visible = fields.Boolean(string="Unit margin is visible",
                                               compute="_compute_mf_unit_margin_is_visible")
    mf_unit_margin = fields.Float(string="Unit margin", help="Write an unit margin coefficient", default=0.0,
                                  digits=dp.get_precision("Price technical"))
    mf_unit_sale_price = fields.Float(string="Unit sale price", compute="_compute_unit_sale_price", store=True,
                                      default=0.0, digits=dp.get_precision("Price technical"))
    mf_hour_sale_price = fields.Float(string="Hour sale price", compute="_compute_hour_sale_price", store=True,
                                      default=0.0, digits=dp.get_precision("Price technical"))
    mf_total_cost_price = fields.Float(string="Total cost price", compute="_compute_total_cost_price", store=True,
                                       default=0.0, digits=dp.get_precision("Price technical"))
    mf_total_margin = fields.Float(string="Total margin", compute="_compute_total_margin", store=True, default=0.0,
                                   digits=dp.get_precision("Price technical"))
    mf_total_sale_price = fields.Float(string="Total sale price", compute="_compute_total_sale_price", store=True,
                                       default=0.0, digits=dp.get_precision("Price technical"))
    
    # ===========================================================================
    # METHODS - FORM ONCHANGES
    # ===========================================================================

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

    # ===========================================================================
    # METHODS - FORM COMPUTE
    # ===========================================================================

    def _get_field_value_if_visible(self, field_name, value_if_invisible=0):
        if field_name in self.env["mf.simulation.config"].get_configurable_simulation_fields_names_list():
            field_is_visible = self._is_configurable_field_visible(field_name)
            if field_is_visible:
                return getattr(self, field_name)
            else:
                return value_if_invisible

    def _is_configurable_field_visible(self, field_name):
        for configurable_field in self.mf_simulation_id.mf_field_configs_ids:
            if configurable_field.mf_field_id.name == field_name:
                return configurable_field.mf_is_visible
        raise MissingError(field_name + _(" is not a configurable field."))

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_mf_price_material_and_consumable(self):
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
        self.mf_unit_cost_price = self.mf_price_material + self._get_field_value_if_visible("mf_price_consumable") \
            + self._get_field_value_if_visible("mf_price_subcontracting") \
            + self._get_field_value_if_visible("mf_price_workforce") \
            + self._get_field_value_if_visible("mf_general_costs")

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_unit_sale_price(self):
        self.mf_unit_sale_price = self.mf_unit_cost_price * self._get_field_value_if_visible("mf_unit_margin", 1)

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_hour_sale_price(self):
        self.mf_hour_sale_price = self.mf_price_workforce * self._get_field_value_if_visible("mf_unit_margin", 1)

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_total_cost_price(self):
        self.mf_total_cost_price = self.mf_unit_cost_price * self.mf_quantity

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_total_margin(self):
        self.mf_total_margin = self.mf_total_sale_price - self.mf_total_cost_price

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id", "mf_general_costs", "mf_unit_margin")
    def _compute_total_sale_price(self):
        self.mf_total_sale_price = self.mf_unit_sale_price * self.mf_quantity

    # ===========================================================================
    # METHODS - VIEW COLUMNS COMPUTE
    # ===========================================================================

    @api.one
    @api.depends("sequence")
    def _compute_mf_price_consumable_is_visible(self):
        self.mf_price_consumable_is_visible = self._get_field_visibility_status_by_name("mf_price_consumable")

    @api.one
    @api.depends("sequence")
    def _compute_mf_price_subcontracting_is_visible(self):
        self.mf_price_subcontracting_is_visible = self._get_field_visibility_status_by_name("mf_price_subcontracting")

    @api.one
    @api.depends("sequence")
    def _compute_mf_price_workforce_is_visible(self):
        self.mf_price_workforce_is_visible = self._get_field_visibility_status_by_name("mf_price_workforce")

    @api.one
    @api.depends("sequence")
    def _compute_mf_general_costs_is_visible(self):
        self.mf_general_costs_is_visible = self._get_field_visibility_status_by_name("mf_general_costs")

    @api.one
    @api.depends("sequence")
    def _compute_mf_unit_margin_is_visible(self):
        self.mf_unit_margin_is_visible = self._get_field_visibility_status_by_name("mf_unit_margin")

    def _get_field_visibility_status_by_name(self, field_name):
        for field_config_id in self.mf_simulation_id.mf_field_configs_ids:
            if field_config_id.mf_field_id.name == field_name:
                return field_config_id.mf_is_visible
        raise MissingError(field_name + _(" is not a configurable field."))
