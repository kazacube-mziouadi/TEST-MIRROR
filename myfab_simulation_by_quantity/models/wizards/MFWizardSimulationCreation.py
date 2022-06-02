# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import datetime


class MFWizardSimulationCreation(models.TransientModel):
    _name = "mf.wizard.simulation.creation"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    mf_model_to_create_id = fields.Many2one("ir.model", string="Model to create", readonly=1)
    mf_simulation_lines_ids = fields.Many2many("mf.simulation.by.quantity.line",
                                               "mf_wizard_simulation_creation_lines_rel",
                                               "mf_wizard_simulation_creation_id", "mf_simulation_line_id",
                                               copy=True, string="Simulation lines", readonly=1)

    @api.model
    def default_get(self, fields_list):
        res = super(MFWizardSimulationCreation, self).default_get(fields_list=fields_list)
        res["mf_model_to_create_id"] = self.env.context.get("mf_model_to_create_id")
        res["mf_simulation_lines_ids"] = self.env.context.get("mf_simulation_lines_ids")
        return res

    @api.multi
    def action_multi_creation(self):
        model_line_field_id = self.get_model_line_field_id()
        partner_id = self.mf_simulation_lines_ids[0].mf_simulation_id.mf_customer_id
        for index, simulation_line_id in enumerate(self.mf_simulation_lines_ids):
            record_to_create_dict = self.get_common_fields_dict(partner_id)
            # Ex: in sale.order, model_line_field_id.name will be "order_line_ids"
            record_to_create_dict[model_line_field_id.name] = [
                self.get_line_creation_dict_for_simulation_line(simulation_line_id, index)
            ]
            if self.mf_model_to_create_id.model == "sale.order":
                record_to_create_dict.update(self.get_sale_order_fields_dict(partner_id))
            elif self.mf_model_to_create_id.model == "quotation":
                record_to_create_dict.update(self.get_quotation_fields_dict(partner_id))
            self.env[self.mf_model_to_create_id.model].create(record_to_create_dict)

    @api.multi
    def action_single_creation(self):
        model_line_field_id = self.get_model_line_field_id()
        partner_id = self.mf_simulation_lines_ids[0].mf_simulation_id.mf_customer_id
        record_to_create_dict = self.get_common_fields_dict(partner_id)
        record_to_create_dict[model_line_field_id.name] = []
        if self.mf_model_to_create_id.model == "sale.order":
            record_to_create_dict.update(self.get_sale_order_fields_dict(partner_id))
        elif self.mf_model_to_create_id.model == "quotation":
            record_to_create_dict.update(self.get_quotation_fields_dict(partner_id))
        for index, simulation_line_id in enumerate(self.mf_simulation_lines_ids):
            # Ex: in sale.order, model_line_field_id.name will be "order_line_ids"
            record_to_create_dict[model_line_field_id.name].append(
                self.get_line_creation_dict_for_simulation_line(simulation_line_id, index)
            )
        self.env[self.mf_model_to_create_id.model].create(record_to_create_dict)

    """
        Returns the relational ir.field corresponding to the one2many lines of the current model
        Ex : For model sale.order, returns it's field order_line_ids  
    """
    def get_model_line_field_id(self):
        return self.env["ir.model.fields"].search([
            ("model_id", '=', self.mf_model_to_create_id.id),
            ("relation", "like", self.mf_model_to_create_id.model),
            ("relation", "like", "line"),
            ("name", "not like", "draft"),
        ])

    """
        Returns a dict containing the common fields of the possible models (sale.order & quotation for now) 
    """
    @staticmethod
    def get_common_fields_dict(partner_id):
        return {
            "partner_id": partner_id.id,
            "currency_id": partner_id.currency_id.id,
            "payment_term_id": partner_id.property_payment_term_id.id,
        }

    """
        Returns a dict containing the sale order fields required for creation (and not contained in common fields dict)
    """
    def get_sale_order_fields_dict(self, partner_id):
        return {
            "order_address_id": partner_id.address_id.id,
            "invoicing_address_id": partner_id.address_id.id,
            "invoicing_method_id": partner_id.sale_invoicing_method_id.id,
            "invoiced_customer_id": partner_id.id,
            "paid_customer_id": partner_id.id,
            "payment_id": partner_id.sale_payment_method_id.id,
            "delivered_address_id": partner_id.delivery_address_ids[0].id if partner_id.delivery_address_ids else partner_id.address_id.id,
            "delivered_name": partner_id.name,
            "sale_account_system_id": partner_id.property_account_position_id.id,
            "delivered_country_id": partner_id.delivery_address_ids[0].country_id.id if partner_id.delivery_address_ids else partner_id.address_id.country_id.id,
            "location_id": partner_id.customer_location_id.id if partner_id.customer_location_id else self.get_random_location_id(),
            "delivered_customer_id": partner_id.id,
        }

    """
        Returns a dict containing the quotation fields required for creation (and not contained in common fields dict)
    """
    @staticmethod
    def get_quotation_fields_dict(partner_id):
        return {
            "quotation_account_system_id": partner_id.property_account_position_id.id,
            "partner_name": partner_id.name,
            "partner_country_id": partner_id.delivery_address_ids[0].country_id.id if partner_id.delivery_address_ids else partner_id.address_id.country_id.id,
        }

    def get_line_creation_dict_for_simulation_line(self, simulation_line_id, index):
        product_id = simulation_line_id.mf_product_id
        creation_fields_dict = {
            "sequence": index + 1,
            "product_id": product_id.id,
            "uoi_id": product_id.uos_id.id if product_id.uos_id else product_id.uom_id.id,
            "price_unit": simulation_line_id.mf_unit_sale_price,
            "uoi_qty": simulation_line_id.mf_quantity,
        }
        if self.mf_model_to_create_id.model == "sale.order":
            creation_fields_dict.update({
                "name": product_id.name,
                "sec_uom_qty": simulation_line_id.mf_quantity,
                "uom_qty": simulation_line_id.mf_quantity,
                "supply_method": "without_stock",  # TODO: correct value ?
                "sec_uom_id": product_id.sec_uom_id.id if product_id.sec_uom_id else product_id.uom_id.id,
                "requested_date": datetime.datetime.now(),
                "uom_id": product_id.uom_id.id,
            })
        elif self.mf_model_to_create_id.model == "quotation":
            creation_fields_dict.update({
                "comment": product_id.name,
                "taxes_ids": [(6, 0, [sale_tax.id for sale_tax in product_id.sale_taxes_ids])]
            })
        else:
            raise ValueError(_("The generation can not be executed on the model ") + self.mf_model_to_create_id.model)
        return (0, 0, creation_fields_dict)

    def get_random_location_id(self):
        location_id = self.env["stock.location"].search([], None, 1)
        return location_id.id
