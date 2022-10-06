from openerp import models, fields, api, _, modules
import openerp.addons.decimal_precision as dp
from openerp.exceptions import MissingError

RESOURCE_CATEGORY_LABEL_SUBCONTRACTING = _("Subcontracting")
RESOURCE_CATEGORY_LABEL_ROUTING_COST = _("Routing cost")
CONFIGURABLE_SIMULATION_FIELDS_NAMES_LIST = [
    "mf_material_unit_price",
    "mf_material_total_price",
    "mf_material_unit_prcnt_margin",
    "mf_material_unit_amount_margin",
    "mf_consumable_unit_price",
    "mf_workforce_unit_price",
    "mf_workforce_unit_price",
    "mf_workforce_total_price",
    "mf_workforce_unit_prcnt_margin",
    "mf_workforce_unit_amount_margin",
    "mf_subcontracting_unit_price",
    "mf_free_costs",
    "mf_unit_prcnt_margin",
    "mf_unit_amount_margin",
]


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

    # ===========================================================================
    # COLUMNS - CALCULATED (readonly)
    # ===========================================================================
    mf_material_unit_price = fields.Float(string="Material unit price", compute="_compute_mf_material_and_consumable_prices", store=True, digits=dp.get_precision("Price technical"))
    mf_material_total_price = fields.Float(string="Material total price", compute="_compute_mf_material_and_consumable_prices", store=True, digits=dp.get_precision("Price technical"))
    mf_material_unit_margin_price = fields.Float(string="Material unit margin price", compute="_compute_mf_material_margin_prices", store=True, digits=dp.get_precision("Price technical"))
    mf_material_total_margin_price = fields.Float(string="Material total margin price", compute="_compute_mf_material_margin_prices", store=True, digits=dp.get_precision("Price technical"))
    mf_consumable_unit_price = fields.Float(string="Consumable unit price", default=0.0, compute="_compute_mf_material_and_consumable_prices", store=True, digits=dp.get_precision("Price technical"))
    mf_consumable_total_price = fields.Float(string="Consumable total price", default=0.0, compute="_compute_mf_material_and_consumable_prices", store=True, digits=dp.get_precision("Price technical"))
    mf_workforce_unit_price = fields.Float(string="Workforce unit price", default=0.0, compute="_compute_mf_workforce_prices", store=True, digits=dp.get_precision("Price technical"))
    mf_workforce_total_price = fields.Float(string="Workforce total price", default=0.0, compute="_compute_mf_workforce_prices", store=True, digits=dp.get_precision("Price technical"))
    mf_workforce_unit_margin_price = fields.Float(string="Workforce unit margin price", compute="_compute_mf_workforce_margin_prices", store=True, digits=dp.get_precision("Price technical"))
    mf_workforce_total_margin_price = fields.Float(string="Workforce total margin price", compute="_compute_mf_workforce_margin_prices", store=True, digits=dp.get_precision("Price technical"))
    mf_hour_sale_price = fields.Float(string="Hour sale price", compute="_compute_hour_sale_price", store=True, default=0.0, digits=dp.get_precision("Price technical"))
    mf_subcontracting_unit_price = fields.Float(string="Subcontracting price", default=0.0, compute="_compute_mf_subcontracting_prices", store=True, digits=dp.get_precision("Price technical"))
    mf_unit_cost_price = fields.Float(string="Unit cost price", compute="_compute_cost_prices", store=True, default=0.0, digits=dp.get_precision("Price technical"))
    mf_total_cost_price = fields.Float(string="Total cost price", compute="_compute_cost_prices", store=True, default=0.0, digits=dp.get_precision("Price technical"))
    mf_unit_sale_price = fields.Float(string="Unit sale price", compute="_compute_sale_prices", store=True, default=0.0, digits=dp.get_precision("Price technical"))
    mf_total_sale_price = fields.Float(string="Total sale price", compute="_compute_sale_prices", store=True, default=0.0, digits=dp.get_precision("Price technical"))
    mf_total_margin = fields.Float(string="Total margin", compute="_compute_total_margin", store=True, default=0.0, digits=dp.get_precision("Price technical"))
    # ===========================================================================
    # COLUMNS - VISIBILITY CALCULATED (readonly)
    # ===========================================================================
    mf_material_unit_price_is_visible = fields.Boolean(string="Material unit price is visible",)
    mf_material_total_price_is_visible = fields.Boolean(string="Material total price is visible")
    mf_material_unit_prcnt_margin_is_visible = fields.Boolean(string="Material unit margin percentage is visible")
    mf_material_unit_amount_margin_is_visible = fields.Boolean(string="Material unit margin amount is visible")
    mf_consumable_unit_price_is_visible = fields.Boolean(string="Consumable price is visible")
    mf_workforce_unit_price_is_visible = fields.Boolean(string="Workforce unit price is visible")
    mf_workforce_total_price_is_visible = fields.Boolean(string="Workforce total price is visible")
    mf_workforce_unit_prcnt_margin_is_visible = fields.Boolean(string="Workforce unit margin percentage is visible")
    mf_workforce_unit_amount_margin_is_visible = fields.Boolean(string="Workforce unit margin amount is visible")
    mf_subcontracting_unit_price_is_visible = fields.Boolean(string="Subcontracting price is visible")
    mf_free_costs_is_visible = fields.Boolean(string="Free costs is visible")
    mf_unit_prcnt_margin_is_visible = fields.Boolean(string="Unit margin percentage is visible")
    mf_unit_amount_margin_is_visible = fields.Boolean(string="Unit margin amount is visible")
    # ===========================================================================
    # COLUMNS - MARGINS (READ / WRITE)
    # ===========================================================================
    mf_material_unit_prcnt_margin = fields.Float(string="Material margin (%)", help="Write a material unit margin percentage", default=0.0, digits=dp.get_precision("Price technical"))
    mf_material_unit_amount_margin = fields.Float(string="Material margin amount", help="Write a material unit margin amount", default=0.0, digits=dp.get_precision("Price technical"))
    mf_workforce_unit_prcnt_margin = fields.Float(string="Workforce margin (%)", help="Write a workforce unit margin percentage", default=0.0, digits=dp.get_precision("Price technical"))
    mf_workforce_unit_amount_margin = fields.Float(string="Workforce margin amount", help="Write a workforce unit margin amount", default=0.0, digits=dp.get_precision("Price technical"))
    mf_unit_prcnt_margin = fields.Float(string="Unit margin (%)", help="Write an unit margin percentage", default=0.0, digits=dp.get_precision("Price technical"))
    mf_unit_amount_margin = fields.Float(string="Unit margin amount", help="Write an unit margin amount", default=0.0, digits=dp.get_precision("Price technical"))
    # ===========================================================================
    # COLUMNS (READ / WRITE)
    # ===========================================================================
    mf_free_costs = fields.Float(string="Free costs", default=0.0, digits=dp.get_precision("Price technical"))
    
    @staticmethod
    def get_configurable_simulation_fields_names_list():
        return CONFIGURABLE_SIMULATION_FIELDS_NAMES_LIST

    # ===========================================================================
    # METHODS - VIEW COLUMNS COMPUTE
    # ===========================================================================
    @api.one
    @api.onchange('sequence')
    def compute_mf_field_is_visible(self):
        vals = {}
        for field in self.get_configurable_simulation_fields_names_list():
            vals[field + '_is_visible'] = self._is_configurable_field_visible(field)
        self.write(vals)

    def _get_field_value_if_visible(self, field_name, value_if_invisible=0):
        if field_name in self.get_configurable_simulation_fields_names_list():
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

    # ===========================================================================
    # METHODS - ONCHANGES
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
    # METHODS - SIMULATIE QUANTITY PRICES
    # ===========================================================================
    
    # Pas de write de plusieurs valeurs d'un coup !
    # Cela genere une erreur lors de la compilation (maximum recursion depth exceeded)

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id")
    def _compute_mf_material_and_consumable_prices(self):
        material_unit_price, ptb, pucb, consumable_unit_price, pur1, puf1 = self.mf_bom_id.function_compute_price(
            button=False,
            type=self.mf_bom_id.type,
            product=self.mf_product_id,
            serie_eco=self.mf_quantity,
            prod_family=self.mf_bom_id.prod_family_id,
            return_detail_price=True,
            product_rc=self.mf_product_id,
            bom_rc=self.mf_bom_id
        )
        self.mf_material_unit_price = material_unit_price
        self.mf_material_total_price = self.mf_material_unit_price * self.mf_quantity
        self.mf_consumable_unit_price = consumable_unit_price
        self.mf_consumable_total_price = self.mf_consumable_unit_price * self.mf_quantity

    @api.one
    @api.depends("mf_consumable_unit_price")
    def _compute_mf_workforce_prices(self):
        qty = self.mf_quantity
        if not qty: qty = 1
        self.mf_workforce_unit_price = self.mf_consumable_unit_price / qty
        self.mf_workforce_total_price = self.mf_workforce_unit_price * self.mf_quantity

    @api.one
    @api.depends("mf_quantity", "mf_product_id", "mf_bom_id", "mf_routing_id")
    def _compute_mf_subcontracting_prices(self):
        # TODO : ce champ est cache le temps que le besoin soit affine
        self.mf_subcontracting_unit_price = 0

    @api.one
    @api.depends("mf_material_unit_price", "mf_material_unit_prcnt_margin", "mf_material_unit_amount_margin")
    def _compute_mf_material_margin_prices(self):
        self.mf_material_unit_margin_price = (
            self.mf_material_unit_price * (1 + self._get_field_value_if_visible("mf_material_unit_prcnt_margin") / 100) 
            + self._get_field_value_if_visible("mf_material_unit_amount_margin")
        ) 
        self.mf_material_total_margin_price = self.mf_material_unit_margin_price * self.mf_quantity

    @api.one
    @api.depends("mf_workforce_unit_price", "mf_workforce_unit_prcnt_margin", "mf_workforce_unit_amount_margin")
    def _compute_mf_workforce_margin_prices(self):
        self.mf_workforce_unit_margin_price = (
            self.mf_workforce_unit_price * (1 + self._get_field_value_if_visible("mf_workforce_unit_prcnt_margin") / 100) 
            + self._get_field_value_if_visible("mf_workforce_unit_amount_margin")
        ) 
        self.mf_workforce_total_margin_price = self.mf_workforce_unit_price * self.mf_quantity

    @api.one
    @api.depends("mf_material_unit_margin_price", "mf_consumable_unit_price", "mf_workforce_unit_margin_price", "mf_free_costs")
    def _compute_cost_prices(self):
        self.mf_unit_cost_price = (
            self.mf_material_unit_margin_price
            + self.mf_consumable_unit_price
            + self.mf_workforce_unit_margin_price
            + self._get_field_value_if_visible("mf_free_costs")
            + self.mf_subcontracting_unit_price
        )
        self.mf_total_cost_price = self.mf_unit_cost_price * self.mf_quantity

    @api.one
    @api.depends("mf_unit_cost_price", "mf_unit_prcnt_margin", "mf_unit_amount_margin")
    def _compute_sale_prices(self):
        self.mf_unit_sale_price = (
            self.mf_unit_cost_price * (1 + self._get_field_value_if_visible("mf_unit_prcnt_margin") / 100)
            + self._get_field_value_if_visible("mf_unit_amount_margin")
        )
        self.mf_total_sale_price = self.mf_unit_sale_price * self.mf_quantity

    @api.one
    @api.depends("mf_workforce_unit_margin_price", "mf_unit_prcnt_margin", "mf_unit_amount_margin")
    def _compute_hour_sale_price(self):
        self.mf_hour_sale_price = (
            self.mf_workforce_unit_margin_price * (1 + self._get_field_value_if_visible("mf_unit_prcnt_margin") / 100)
            + self._get_field_value_if_visible("mf_unit_amount_margin")
        )   

    @api.one
    @api.depends("mf_total_sale_price")
    def _compute_total_margin(self):
        self.mf_total_margin = self.mf_total_sale_price - self.mf_total_cost_price