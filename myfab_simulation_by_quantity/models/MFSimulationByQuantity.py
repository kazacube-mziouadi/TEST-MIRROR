from openerp import models, fields, api, _, modules
from openerp.exceptions import MissingError


class MFSimulationByQuantity(models.Model):
    _name = "mf.simulation.by.quantity"
    _description = "myfab Simulation by quantity"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, readonly=True)
    mf_designation = fields.Char(string="Designation", size=60, required=True)
    mf_description = fields.Text(string="Description")
    mf_customer_id = fields.Many2one("res.partner", string="Customer")
    mf_product_id = fields.Many2one("product.product", string="Product", required=True)
    mf_bom_id = fields.Many2one("mrp.bom", string="Nomenclature", required=True)
    mf_routing_id = fields.Many2one("mrp.routing", string="Routing", required=True)
    mf_simulation_lines_ids = fields.One2many("mf.simulation.by.quantity.line", "mf_simulation_id", copy=True, string="Simulation lines")
    mf_field_configs_ids = fields.One2many("mf.simulation.config.field", "mf_simulation_id", string="Configurable fields")
    mf_display_warning_config_message = fields.Boolean(default=False)

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
        fields_list["mf_field_configs_ids"] = self._get_field_configs_ids_from_global_config()

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
            fields_list["mf_display_warning_config_message"] = False
        res = super(MFSimulationByQuantity, self).write(fields_list)
        if "mf_field_configs_ids" in fields_list:
            self.recompute_simulation_lines_button()
        return res

    @api.one
    def mf_fields_update(self):
        fields_list = {
                'mf_field_configs_ids': self._get_field_configs_ids_from_global_config(),
            }
        self.write(fields_list)
        self._set_fields_order()

    def _get_field_configs_ids_from_global_config(self):
        global_config_field_ids = self._get_global_config_fields()
        field_configs_ids_list = []
        field_names_present_in_list = []
        for config_field in self.mf_field_configs_ids:
            field_names_present_in_list.append(config_field.mf_field_id.name)

        for field_config_id in global_config_field_ids:
            if field_config_id.mf_field_id.name not in field_names_present_in_list:
                field_configs_ids_list.append((0, 0, {
                    "sequence": field_config_id.sequence,
                    "mf_field_id": field_config_id.mf_field_id.id,
                    "mf_is_visible": field_config_id.mf_is_visible,
                }))

        return field_configs_ids_list

    def _get_global_config_fields(self):
        global_config_id = self.env["mf.simulation.config"].search([], None, 1)
        if not global_config_id:
            global_config_id = self.env["mf.simulation.config"].create({})
        else:
            global_config_id.mf_update()

        return global_config_id.mf_fields_ids
    
    def _set_fields_order(self):
        global_config_field_ids = self._get_global_config_fields()
        for global_field_id in global_config_field_ids:
            for field_config_id in self.mf_field_configs_ids:
                if field_config_id.mf_field_id.id == global_field_id.mf_field_id.id:
                    field_config_id.sequence = global_field_id.sequence

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
        self.mf_display_warning_config_message = True

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
            "name": _("Simulation by quantity - Lines export"),
            "view_mode": "form",
            "res_model": "mf.wizard.simulation.generic.creation",
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
            simulation_line_id.compute_mf_field_is_visible()
            simulation_line_id.mf_quantity = simulation_line_id.mf_quantity

    @api.multi
    def update_product_customer_info_button(self):
        self.check_customer_and_lines_exist()
        simulation_lines_to_create_ids = self.env["mf.simulation.by.quantity.line"].search([
            ("mf_simulation_id", '=', self.id), ("mf_selected_for_creation", '=', True)
        ])
        return {
            "name": _("Simulation by quantity - Product info update"),
            "view_mode": "form",
            "res_model": "mf.wizard.simulation.product.info.creation",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {
                "mf_customer_id": self.mf_customer_id.id,
                "mf_simulation_lines_ids": [simulation_line.id for simulation_line in simulation_lines_to_create_ids]
            }
        }

    def check_customer_and_lines_exist(self):
        if (not self.mf_customer_id 
            or not self.mf_simulation_lines_ids
            or not self.at_least_one_simulation_line_is_selected()
        ):
            raise MissingError(_(
                "Make sure that a customer is selected and that the simulation contains at least one selected line."
            ))

    def at_least_one_simulation_line_is_selected(self):
        for simulation_line_id in self.mf_simulation_lines_ids:
            if simulation_line_id.mf_selected_for_creation:
                return True
        return False
