# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


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
    def action_single_creation(self):
        model_line_field_id = self.env["ir.model.fields"].search([
            ("model_id", '=', self.mf_model_to_create_id.id),
            ("relation", "like", self.mf_model_to_create_id.model),
            ("name", "like", "line"),
        ])
        partner_id = self.mf_simulation_lines_ids[0].mf_simulation_id.mf_customer_id
        for simulation_line_id in self.mf_simulation_lines_ids:
            record_to_create_dict = {
                "partner_id": partner_id.id,
                model_line_field_id.name: [self.get_line_creation_dict_for_simulation_line(simulation_line_id)]
            }
            if self.mf_model_to_create_id.model == "sale.order":
                record_to_create_dict.update({
                    "order_address_id": partner_id.address_id.id,
                    "invoicing_address_id": partner_id.address_id.id,
                    "invoicing_method_id": partner_id.sale_invoicing_method_id.id,
                    "currency_id": partner_id.currency_id.id,
                    "invoiced_customer_id": partner_id.id,
                    "paid_customer_id": partner_id.id,
                    "payment_id": partner_id.sale_payment_method_id.id,
                    "delivered_address_id": partner_id.delivery_address_ids[0].id if partner_id.delivery_address_ids else partner_id.address_id.id,
                    "payment_term_id": partner_id.property_payment_term_id.id,
                    "delivered_name": partner_id.name,
                    "sale_account_system_id": partner_id.property_account_position_id.id,
                    "delivered_country_id": partner_id.delivery_address_ids[0].country_id.id if partner_id.delivery_address_ids else partner_id.address_id.country_id.id,
                    "location_id": partner_id.customer_location_id.id if partner_id.customer_location_id else self.get_random_location_id(),
                    "delivered_customer_id": partner_id.id,
                })
            print("*****")
            print(record_to_create_dict)
            self.env[self.mf_model_to_create_id.model].create(record_to_create_dict)

    @api.multi
    def action_multi_creation(self):
        pass

    @staticmethod
    def get_line_creation_dict_for_simulation_line(simulation_line_id):
        return (0, 0, {
            "name": simulation_line_id.mf_product_id.name,
            "product_id": simulation_line_id.mf_product_id.id,
            "sec_uom_qty": simulation_line_id.mf_quantity,
            "price_unit": simulation_line_id.mf_unit_sale_price,
            "supply_method": "without_stock",  # TODO ?
            "sec_uom_id": simulation_line_id.mf_product_id.sec_uom_id.id if simulation_line_id.mf_product_id.sec_uom_id else simulation_line_id.mf_product_id.uom_id.id,
        })

    def get_random_location_id(self):
        location_id = self.env["stock.location"].search([], None, 1)
        return location_id.id