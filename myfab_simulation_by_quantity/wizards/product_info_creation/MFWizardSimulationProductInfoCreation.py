# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import timedelta, datetime


class MFWizardSimulationProductInfoCreation(models.TransientModel):
    _name = "mf.wizard.simulation.product.info.creation"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    mf_product_info_lines_start_date = fields.Date(string="Inserted product info lines start date", required=True)
    mf_customer_id = fields.Many2one("res.partner", string="Customer linked to product info lines", readonly=1)
    mf_simulation_lines_ids = fields.Many2many("mf.simulation.by.quantity.line",
                                               "mf_wizard_simulation_product_info_creation_lines_rel",
                                               "mf_wizard_simulation_product_info_creation_id", "mf_simulation_line_id",
                                               copy=True, string="Inserted simulation lines", readonly=1)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.model
    def default_get(self, fields_list):
        res = super(MFWizardSimulationProductInfoCreation, self).default_get(fields_list=fields_list)
        res["mf_customer_id"] = self.env.context.get("mf_customer_id")
        res["mf_simulation_lines_ids"] = self.env.context.get("mf_simulation_lines_ids")
        return res

    @api.multi
    def action_product_info_creation(self):
        # One line case : no need to sort, we append directly the customer info and it's price within
        if len(self.mf_simulation_lines_ids) < 2:
            self.append_customer_info_line_to_product(
                self.mf_simulation_lines_ids[0].mf_product_id,
                [self.get_product_price_creation_dict(self.mf_simulation_lines_ids[0])]
            )
            return
        # Multi lines case
        # We sort the selected simulation lines list on the products' ids (for optimisation sake)
        simulation_lines_ids_sorted_on_product_id_list = sorted(
            self.mf_simulation_lines_ids,
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

    def get_product_price_creation_dict(self, simulation_line_id):
        return {
            "date_start": self.str_to_date(self.mf_product_info_lines_start_date),
            "min_qty": simulation_line_id.mf_quantity,
            "price": simulation_line_id.mf_unit_sale_price,
        }

    def append_customer_info_line_to_product(self, product_id, product_prices_list):
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
            "internal_note": _("Generated from the myfab simulation by quantity ") + self.mf_simulation_lines_ids[0].mf_simulation_id.name
        })]

    def end_prices_today_when_possible(self, customer_info_id):
        day_before_chosen_date = self.str_to_date(self.mf_product_info_lines_start_date) - timedelta(days=1)
        for price_id in customer_info_id.pricelist_ids:
            if not price_id.date_start:
                continue
            price_date_start = self.str_to_date(price_id.date_start)
            if price_date_start <= day_before_chosen_date and not price_id.date_stop:
                price_id.date_stop = day_before_chosen_date

    def merge_product_prices_list_in_customer_info(self, product_prices_list, customer_info_id):
        product_prices_list_indexes_to_pop = []
        for index, product_price_tuple in enumerate(product_prices_list):
            prices_with_same_quantity_ids_list = self.get_prices_with_same_quantity_ids_list(
                customer_info_id.pricelist_ids, product_price_tuple
            )
            if len(prices_with_same_quantity_ids_list) > 0:
                success = self.set_dates_on_price_line_creation_tuple_depending_on_existing_lines_with_same_quantity(
                    product_price_tuple, prices_with_same_quantity_ids_list
                )
                # The price line creation is impossible : we pop it's tuple from the list
                if not success:
                    product_prices_list_indexes_to_pop.append(index)
        product_prices_list_indexes_to_pop_reversed = sorted(product_prices_list_indexes_to_pop, reverse=True)
        for product_price_list_index_to_pop in product_prices_list_indexes_to_pop_reversed:
            product_prices_list.pop(product_price_list_index_to_pop)

    @staticmethod
    def get_prices_with_same_quantity_ids_list(prices_ids_list, price_creation_dict):
        prices_with_same_quantity_ids_list = []
        for price_id in prices_ids_list:
            if price_id.min_qty == price_creation_dict[2]["min_qty"]:
                prices_with_same_quantity_ids_list.append(price_id)
        return prices_with_same_quantity_ids_list

    """
        Set the date_start and date_stop of the line depending on the date_start and date_stop of the existing lines.
        Returns True if the dates have been set, else False (impossible line creation case).
    """
    def set_dates_on_price_line_creation_tuple_depending_on_existing_lines_with_same_quantity(
            self, price_creation_tuple, prices_with_same_quantity_ids_list
    ):
        price_creation_dict = price_creation_tuple[2]
        prices_with_same_quantity_ids_sorted_list = sorted(
            prices_with_same_quantity_ids_list, key=lambda price_id: price_id.date_stop
        )
        # First loop : we set the price line's date_start between all existing prices for this quantity
        for price_with_same_quantity_id in prices_with_same_quantity_ids_sorted_list:
            # Convert the date start and the date stop (if instantiated) to datetime.date
            price_with_same_quantity_date_start = self.str_to_date(
                price_with_same_quantity_id.date_start
            ) if price_with_same_quantity_id.date_start else None
            price_with_same_quantity_date_stop = self.str_to_date(
                price_with_same_quantity_id.date_stop
            ) if price_with_same_quantity_id.date_stop else None
            # Exclusion case : we can not create the new line in the below conditions
            if price_with_same_quantity_date_start and (
                    price_with_same_quantity_date_start <= price_creation_dict["date_start"]
            ) and not price_with_same_quantity_id.date_stop:
                return False
            # Check overlapping rules
            if (
                    price_with_same_quantity_date_stop and (
                    price_creation_dict["date_start"] <= price_with_same_quantity_date_stop
            )
            ) and (
                    not price_with_same_quantity_date_start or (
                    price_with_same_quantity_date_start <= price_creation_dict["date_start"]
            )
            ):
                price_creation_dict["date_start"] = price_with_same_quantity_date_stop + timedelta(days=1)
        # Second loop : we set the price line's date_stop before all existing prices for this quantity
        for price_with_same_quantity_id in prices_with_same_quantity_ids_sorted_list:
            price_with_same_quantity_date_start = self.str_to_date(
                price_with_same_quantity_id.date_start
            ) if price_with_same_quantity_id.date_start else None
            # Exclusion case : we can not create the new line in the below conditions
            if price_with_same_quantity_date_start and (
                    price_with_same_quantity_date_start <= price_creation_dict["date_start"]
            ) and not price_with_same_quantity_id.date_stop:
                return False
            # Check overlapping rules
            if price_with_same_quantity_date_start and (
                    price_creation_dict["date_start"] <= price_with_same_quantity_date_start
            ):
                price_creation_dict["date_stop"] = price_with_same_quantity_date_start - timedelta(days=1)
        return True

    @staticmethod
    def str_to_date(date_str):
        if type(date_str) is str:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            return date_str
