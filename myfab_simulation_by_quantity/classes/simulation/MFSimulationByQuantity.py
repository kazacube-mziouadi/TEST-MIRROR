from openerp import models, fields, api, _, modules
from openerp.exceptions import MissingError
import datetime


class MFSimulationByQuantity(models.Model):
    _name = "mf.simulation.by.quantity"
    _description = "myfab Simulation by quantity"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, readonly=True)
    mf_designation = fields.Char(string="Designation", size=60, required=True)
    mf_description = fields.Text(string="Description")
    mf_product_id = fields.Many2one("product.product", string="Product", required=True)
    mf_bom_id = fields.Many2one("mrp.bom", string="Nomenclature", required=True)
    mf_routing_id = fields.Many2one("mrp.routing", string="Routing", required=True)
    mf_simulation_lines_ids = fields.One2many("mf.simulation.by.quantity.line", "mf_simulation_id", copy=True, string="Simulation lines")
    mf_field_configs_ids = fields.One2many("mf.simulation.config.field", "mf_simulation_id", string="Configurable fields")
    mf_display_warning_config_message = fields.Boolean(default=False)
    mf_customer_id = fields.Many2one("res.partner", string="Customer")
    mf_quotation_id = fields.Many2one("quotation", string="Quotation", readonly=True)
    mf_sale_order_id = fields.Many2one("sale.order", string="Sale order", readonly=True)

    # ===========================================================================
    # METHODS - MODEL
    # ===========================================================================
    @api.model
    def default_get(self, fields_list):
        res = super(MFSimulationByQuantity, self).default_get(fields_list=fields_list)
        res["mf_designation"] = self.env.context.get("mf_designation")
        res["mf_product_id"] = self.env.context.get("mf_product_id")
        res["mf_customer_id"] = self.env.context.get("mf_customer_id")

        quotation_line_id_id = self.env.context.get("mf_quotation_line_id")
        if sale_order_line_id_id:
            quotation_line_id = self.env["quotation.line"].search([("id", "=", quotation_line_id_id)])
            if quotation_line_id:
                res["mf_quotation_id"] = quotation_line_id.quotation_id.id
                res["mf_customer_id"] = quotation_line_id.quotation_id.partner_id.id
                res["mf_product_id"] = quotation_line_id.product_id.id

        sale_order_line_id_id = self.env.context.get("mf_sale_order_line_id")
        if sale_order_line_id_id:
            sale_order_line_id = self.env["sale.order.line"].search([("id", "=", sale_order_line_id_id)])
            if sale_order_line_id:
                res["mf_sale_order_id"] = sale_order_line_id.sale_order_id.id
                res["mf_customer_id"] = sale_order_line_id.sale_order_id.partner_id.id
                res["mf_product_id"] = sale_order_line_id.product_id.id

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
            self.recompute_simulation_lines_button(True)
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
                    "mf_is_visible": False,
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
                if field_config_id.mf_field_id.id == global_field_id.mf_field_id.id and field_config_id.sequence != global_field_id.sequence:
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
        return self.open_model_creation_wizard("sale.order", True)

    @api.multi
    def create_quotation_button(self):
        return self.open_model_creation_wizard("quotation")

    def open_model_creation_wizard(self, model_to_create_name, is_for_sale_order = False):
        model_to_create_id = self._mf_get_model(model_to_create_name)
        simulation_lines_to_create_ids = self._get_selected_simulation_lines(is_for_sale_order)
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
    def update_sale_order_button(self):
        simulation_lines_to_create_ids = self._get_selected_simulation_lines(True)
        if self.mf_sale_order_id and simulation_lines_to_create_ids:
            self.mf_action_single_save(self._mf_get_model("sale.order"), self.mf_sale_order_id, simulation_lines_to_create_ids)
        

    @api.multi
    def update_quotation_button(self):
        simulation_lines_to_create_ids = self._get_selected_simulation_lines()
        if self.mf_quotation_id and simulation_lines_to_create_ids:
            self.mf_action_single_save(self._mf_get_model("quotation"), self.mf_quotation_id, simulation_lines_to_create_ids)


    @api.multi
    def recompute_simulation_lines_button(self, compute_field_visible_state = False):
        for simulation_line_id in self.mf_simulation_lines_ids:
            if compute_field_visible_state:
                simulation_line_id.compute_mf_field_is_visible()
            simulation_line_id.mf_quantity = simulation_line_id.mf_quantity

    @api.multi
    def update_product_customer_info_button(self):
        simulation_lines_to_create_ids = self._get_selected_simulation_lines()
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

    def _mf_get_model(self, model_name):
        return self.env["ir.model"].search([("model", '=', model_name)], None, 1)

    def _get_selected_simulation_lines(self, is_for_sale_order = False):
        simulation_lines_ids = []
        for simulation_line in self.mf_simulation_lines_ids:
            if simulation_line.mf_selected_for_creation and (
                not is_for_sale_order 
                or simulation_line.mf_product_id.state == 'lifeserie'
            ): 
                simulation_lines_ids.append(simulation_line)
        if len(simulation_lines_ids) == 0: 
            simulation_lines_ids = False

        if not self.mf_customer_id or not simulation_lines_ids:
            raise MissingError(_(
                "Make sure that a customer is selected and that the simulation contains at least one selected line."
            ))

        return simulation_lines_ids

    @api.one
    def mf_action_multi_creation(self, model_id, selected_simulation_lines_ids):
        model_line_field_id = self._mf_get_model_line_field_id(model_id)
        partner_id = selected_simulation_lines_ids[0].mf_simulation_id.mf_customer_id
        last_record_created_id = None
        for index, simulation_line_id in enumerate(selected_simulation_lines_ids):
            # Ex: in sale.order, the below key model_line_field_id.name will be "order_line_ids"
            record_to_create_dict = {model_line_field_id.name: [
                self._mf_get_line_creation_dict_for_simulation_line(model_id, simulation_line_id, 1 * 10)
            ]}
            last_record_created_id = self._mf_create_record(model_id, record_to_create_dict, partner_id)
        return self._mf_open_record(model_id, last_record_created_id)

    @api.one
    def mf_action_single_save(self, model_id, model_record_id, selected_simulation_lines_ids):
        max_sequence = self._mf_get_max_sequence(model_id, model_record_id) if model_record_id else 0
        model_line_field_id = self._mf_get_model_line_field_id(model_id)
        partner_id = selected_simulation_lines_ids[0].mf_simulation_id.mf_customer_id
        record_to_create_dict = {model_line_field_id.name: []}
        simulation_lines_ids_sorted_list = sorted(
            selected_simulation_lines_ids, 
            key=lambda simulation_line_id: simulation_line_id.sequence
        )
        for index, simulation_line_id in enumerate(simulation_lines_ids_sorted_list):
            # Ex: in sale.order, model_line_field_id.name will be "order_line_ids"
            record_to_create_dict[model_line_field_id.name].append(
                self._mf_get_line_creation_dict_for_simulation_line(model_id, simulation_line_id, ((1 + index) * 10 + max_sequence))
            )
        if model_record_id:
            model_record_id = self._mf_write_record(model_id, model_record_id, record_to_create_dict, partner_id)
        else:
            model_record_id = self._mf_create_record(model_id, record_to_create_dict, partner_id)
        #TODO : revenir sur le devis / vente d'origine. 
        # En dehors de la wizard la fonction suivante ne fonctionne pas pour l'instant
        return self._mf_open_record(model_id, model_record_id)

    """
        Returns the relational ir.field corresponding to the one2many lines of the current model
        Ex : For model sale.order, returns it's field order_line_ids  
    """
    def _mf_get_model_line_field_id(self, model_id):
        search_filters_list = [
            ("model_id", '=', model_id.id),
            ("relation", "like", model_id.model),
            ("relation", "like", "line"),
        ]
        if model_id.model == "quotation":
            search_filters_list.append(("name", "like", "draft"))
        return self.env["ir.model.fields"].search(search_filters_list)

    @staticmethod
    def _mf_get_max_sequence(model_id, model_record_id):
        seq_list = []
        line_ids = []

        if model_id.model == "sale.order": line_ids = model_record_id.order_line_ids
        elif model_id.model == "quotation": line_ids = model_record_id.draft_quotation_line_ids

        for line in line_ids:
            seq_list.append(line.sequence)

        return max(seq_list or [0])

    def _mf_get_line_creation_dict_for_simulation_line(self, model_id, simulation_line_id, sequence):
        product_id = simulation_line_id.mf_product_id
        creation_fields_dict = {
            "sequence": sequence,
            "product_id": product_id.id,
            "uoi_id": product_id.uos_id.id if product_id.uos_id else product_id.uom_id.id,
            "price_unit": simulation_line_id.mf_unit_sale_price,
            "uoi_qty": simulation_line_id.mf_quantity,
            "taxes_ids": [(6, 0, [sale_tax.id for sale_tax in product_id.sale_taxes_ids])],
        }
        if model_id.model == "sale.order":
            creation_fields_dict.update({
                "name": product_id.name,
                "sec_uom_qty": simulation_line_id.mf_quantity,
                "uom_qty": simulation_line_id.mf_quantity,
                "supply_method": "without_stock",  # TODO: correct value ?
                "sec_uom_id": product_id.sec_uom_id.id if product_id.sec_uom_id else product_id.uom_id.id,
                "requested_date": datetime.datetime.now(),
                "uom_id": product_id.uom_id.id,
            })
        elif model_id.model == "quotation":
            creation_fields_dict.update({
                "comment": product_id.name,
            })
        else:
            raise ValueError(_("The generation can not be executed on the model ") + model_id.model)
        return (0, 0, creation_fields_dict)
    
    def _mf_create_record(self, model_id, record_to_create_dict, partner_id):
        if model_id.model == "sale.order":
            record_created_id = self.env[model_id.model].with_context(self.env.context.copy()).create_sale(
                customer=partner_id,
                other_data=record_to_create_dict
            )
        elif model_id.model == "quotation":
            record_to_create_dict.update(self._mf_get_quotation_fields_dict(partner_id))
            record_created_id = self.env[model_id.model].create(record_to_create_dict)
            record_created_id.compute_all_taxes()
        return record_created_id

    def _mf_write_record(self, model_id, model_record_id, record_to_create_dict, partner_id):
        if model_id.model == "sale.order":
            model_record_id.write(record_to_create_dict)
        elif model_id.model == "quotation":
            record_to_create_dict.update(self._mf_get_quotation_fields_dict(partner_id))
            model_record_id.write(record_to_create_dict)
            model_record_id.compute_all_taxes()
            
        return model_record_id

    """
        Returns a dict containing the quotation fields required for creation (and not contained in common fields dict)
    """
    @staticmethod
    def _mf_get_quotation_fields_dict(partner_id):
        return {
            "partner_id": partner_id.id,
            "currency_id": partner_id.currency_id.id,
            "payment_term_id": partner_id.property_payment_term_id.id,
            "quotation_account_system_id": partner_id.property_account_position_id.id,
            "partner_name": partner_id.name,
            "partner_country_id": partner_id.delivery_address_ids[0].country_id.id if partner_id.delivery_address_ids else partner_id.address_id.country_id.id,
        }

    def _mf_open_record(self, model_to_create_id, record_id):
        return {
            "view_mode": "form",
            "res_model": model_to_create_id.model,
            "res_id": record_id.id,
            "type": "ir.actions.act_window",
            "target": "current"
        }

    # ===========================================================================
    # METHODS - WIZARD
    # ===========================================================================
    #TODO : revoir le fonctionnement de l'appel de cette wizard.
    # L'ajout de ce traitement dans le modele de la wizard, soit genere des soucis d'affichage de la liste, soit lors de la validation des donnees
    @api.multi
    def global_value(self):
        field_ids_list = self._set_wizard_editable_fields()
        return {
            "name": _("Apply new value on all simulation lines"),
            "view_mode": "form",
            "res_model": "mf.wizard.simulation.global.value",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {
                "mf_simulation_id": self.id,
                "mf_selectable_field_ids": field_ids_list[0] if len(field_ids_list) == 1 else False,
            }
        }

    def _get_editable_simulation_fields_names_list(self):
        model_id = self.env["ir.model"].search([("model", '=', "mf.simulation.by.quantity.line")], None, 1)
        editable_simulation_fields_ids = self.env["ir.model.fields"].search([
            ("name", "in", self.env["mf.simulation.by.quantity.line"].get_editable_simulation_fields_names_list()),
            ("model_id", '=', model_id.id)
        ])
        return editable_simulation_fields_ids

    def _set_wizard_editable_fields(self):
        self.env["mf.wizard.simulation.fields.list"].search([("mf_simulation_id", "=", self.id)]).unlink()

        new_field_ids_list = []
        for field_id in self._get_editable_simulation_fields_names_list():
            for field_config_id in self.mf_field_configs_ids:
                if field_id.name == field_config_id.mf_field_id.name and field_config_id.mf_is_visible:
                    new_field_id = self.env["mf.wizard.simulation.fields.list"].create({
                        "sequence": field_config_id.sequence,
                        "name": field_id.field_description,
                        "mf_technical_name": field_id.name,
                        "mf_simulation_id": self.id,
                    })
                    new_field_ids_list.append(new_field_id.id)

        return new_field_ids_list
