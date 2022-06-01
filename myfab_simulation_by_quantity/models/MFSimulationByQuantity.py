from openerp import models, fields, api, _, modules
from openerp.exceptions import MissingError
from datetime import date, timedelta, datetime


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
    mf_field_configs_ids = fields.One2many("mf.simulation.config.field", "mf_simulation_id",
                                           string="Configurable fields")
    mf_hide_warning_config_message = fields.Boolean("Hide warning config message", default=True)

    # ===========================================================================
    # METHODS - MODEL
    # ===========================================================================
    @api.model
    def default_get(self, fields_list):
        res = super(MFSimulationByQuantity, self).default_get(fields_list=fields_list)
        res["mf_product_id"] = self.env.context.get("mf_product_id")
        return res

    @api.model
    def create(self, fields_list):
        # We write the simulation's name using it's sequence
        fields_list["name"] = self.env["ir.sequence"].get("mf.simulation.by.quantity")
        fields_list["mf_field_configs_ids"] = self.get_field_configs_ids_from_global_config()
        return super(MFSimulationByQuantity, self).create(fields_list)

    @api.multi
    def write(self, fields_list):
        # Check if the fields configuration has been written
        # If so we have to recompute the simulation lines
        if "mf_field_configs_ids" in fields_list:
            # Updating the fields' configurations manually before write (else recompute does not work)
            # Loop through the written fields configurations
            for field_config_write_list in fields_list["mf_field_configs_ids"]:
                # Get the necessary data from writing list
                field_config_id_id = field_config_write_list[1]
                field_config_write_dict = field_config_write_list[2]
                # Continue if no fields have been changed on the field's configuration
                if not field_config_write_dict:
                    continue
                # Loop through the real fields configurations and update the corresponding field's configuration
                for field_config_id in self.mf_field_configs_ids:
                    if field_config_id.id == field_config_id_id:
                        field_config_id.mf_is_visible = field_config_write_dict["mf_is_visible"]
                        break
            self.recompute_simulation_lines_button()
        fields_list["mf_hide_warning_config_message"] = True
        return super(MFSimulationByQuantity, self).write(fields_list)

    def get_field_configs_ids_from_global_config(self):
        global_config_id = self.env["mf.simulation.config"].search([], None, 1)
        field_configs_ids_list = []
        for field_config_id in global_config_id.mf_fields_ids:
            field_configs_ids_list.append((0, 0, {
                "mf_is_visible": field_config_id.mf_is_visible,
                "mf_field_id": field_config_id.mf_field_id.id
            }))
        return field_configs_ids_list

    # ===========================================================================
    # METHODS - ONCHANGE
    # ===========================================================================

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

    @api.onchange("mf_field_configs_ids")
    def _onchange_mf_field_configs_ids(self):
        self.mf_hide_warning_config_message = False

    # ===========================================================================
    # METHODS - BUTTONS
    # ===========================================================================

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
            self.append_customer_info_line_to_product(
                self.mf_simulation_lines_ids[0].mf_product_id,
                [self.get_product_price_creation_dict(self.mf_simulation_lines_ids[0])]
            )
            return
        # Multi lines case
        # We filter the simulation lines to keep only the selected ones
        simulation_lines_ids_selected_list = filter(
            lambda simulation_line: simulation_line.mf_selected_for_creation,
            self.mf_simulation_lines_ids
        )
        # We sort the selected simulation lines list on the products' ids
        simulation_lines_ids_sorted_on_product_id_list = sorted(
            simulation_lines_ids_selected_list,
            key=lambda simulation_line: simulation_line.mf_product_id.id
        )
        previous_simulation_line_id = None
        product_prices_list = []
        for index, simulation_line_id in enumerate(simulation_lines_ids_sorted_on_product_id_list):
            product_id = simulation_line_id.mf_product_id
            # If it's a product not processed yet, we create the product's customer info for the previous product
            if previous_simulation_line_id and previous_simulation_line_id.mf_product_id != product_id:
                self.append_customer_info_line_to_product(
                    previous_simulation_line_id.mf_product_id, product_prices_list
                )
                product_prices_list = []
            # We append the prices of each line for the current product
            product_prices_list.append((0, 0, self.get_product_price_creation_dict(simulation_line_id)))
            # If it's the last line we create the product's customer info with the prices list within
            if index + 1 >= len(simulation_lines_ids_sorted_on_product_id_list):
                self.append_customer_info_line_to_product(
                    simulation_line_id.mf_product_id, product_prices_list
                )
            previous_simulation_line_id = simulation_line_id

    def check_customer_and_lines_exist(self):
        if not self.mf_customer_id or not self.mf_simulation_lines_ids:
            raise MissingError(_(
                "Make sure that a customer is selected and that the simulation contains at least one line."
            ))

    @staticmethod
    def get_product_price_creation_dict(simulation_line_id):
        return {
            "date_start": date.today() + timedelta(days=1),
            "min_qty": simulation_line_id.mf_quantity,
            "price": simulation_line_id.mf_unit_sale_price,
        }

    def append_customer_info_line_to_product(self, product_id, product_prices_list):
        print(product_prices_list)
        # Check if there is already a customer info for this customer ; if so, we merge the lines in it
        for customer_info_id in product_id.cinfo_ids:
            if customer_info_id.partner_id == self.mf_customer_id:
                self.end_prices_today_when_possible(customer_info_id)
                self.merge_product_prices_list_in_customer_info(product_prices_list, customer_info_id)
                customer_info_id.pricelist_ids = product_prices_list
                return
        # Else we create a new customer info for this customer, with the lines in it
        product_id.cinfo_ids = [(0, 0, {
            "sequence": 1,
            "partner_id": self.mf_customer_id.id,
            "state": "development",
            "currency_id": self.mf_customer_id.currency_id.id,
            "company_id": self.env.user.company_id.id,
            "uos_id": product_id.uos_id.id if product_id.uos_id else product_id.uom_id.id,
            "uos_category_id": product_id.uos_id.category_id.id if product_id.uos_id else product_id.uom_id.category_id.id,
            "uoi_id": product_id.sale_uoi_id.id if product_id.sale_uoi_id else product_id.uom_id.id,
            "uom_category_id": product_id.uom_id.category_id.id,
            "multiple_qty": 1.0,
            "pricelist_ids": product_prices_list,
            "internal_note": _("Generate from the myfab simulation by quantity ") + self.name
        })]

    @staticmethod
    def end_prices_today_when_possible(customer_info_id):
        today = date.today()
        for price_id in customer_info_id.pricelist_ids:
            if (not price_id.date_start or datetime.strptime(price_id.date_start, "%Y-%m-%d").date() <= today) and not price_id.date_stop:
                price_id.date_stop = today

    def merge_product_prices_list_in_customer_info(self, product_prices_list, customer_info_id):
        for product_price_dict in product_prices_list:
            prices_with_same_quantity_ids_list = self.get_prices_with_same_quantity_ids_list(
                customer_info_id.pricelist_ids, product_price_dict
            )
            if len(prices_with_same_quantity_ids_list) > 0:
                self.set_date_stop_on_product_price_when_necessary(
                    product_price_dict, prices_with_same_quantity_ids_list
                )

    @staticmethod
    def get_prices_with_same_quantity_ids_list(prices_ids_list, price_creation_dict):
        prices_with_same_quantity_ids_list = []
        for price_id in prices_ids_list:
            if price_id.min_qty == price_creation_dict[2]["min_qty"]:
                prices_with_same_quantity_ids_list.append(price_id)
        return prices_with_same_quantity_ids_list

    @staticmethod
    def set_date_stop_on_product_price_when_necessary(price_creation_tuple, prices_with_same_quantity_ids_list):
        today = str(date.today())
        price_creation_dict = price_creation_tuple[2]
        prices_with_same_quantity_ids_sorted_list = sorted(prices_with_same_quantity_ids_list, key=lambda price_id: price_id.date_stop)
        for price_with_same_quantity_id in prices_with_same_quantity_ids_sorted_list:
            if today < price_with_same_quantity_id.date_stop:
                if "date_stop" not in price_creation_dict or price_with_same_quantity_id.date_stop < price_creation_dict["date_stop"]:
                    price_creation_dict["date_stop"] = str(datetime.strptime(
                        price_with_same_quantity_id.date_stop, "%Y-%m-%d"
                    ).date() - timedelta(days=1))
