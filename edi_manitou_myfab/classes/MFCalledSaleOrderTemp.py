from openerp import models, fields, api, registry, _
import datetime
from calendar import monthrange

MONDAY_WEEK_ORDER = 0
TUESDAY_WEEK_ORDER = 1
WEDNESDAY_WEEK_ORDER = 2
THURSDAY_WEEK_ORDER = 3
FRIDAY_WEEK_ORDER = 4


class MFCalledSaleOrderTemp(models.Model):
    _name = "mf.called.sale.order.temp"
    _description = "myfab temp model of called sales order"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_sale_order_id = fields.Many2one("sale.order", string="Open sale order", required=True)
    mf_product_id = fields.Many2one("product.product", string="Product", required=True)
    mf_delivery_address_id = fields.Many2one("address", string="Delivery address", required=True)
    mf_year_week = fields.Integer(string="Year and week number at format YYYYWW")
    mf_week_month = fields.Integer(string="Week's month number")
    mf_week_first_day_number = fields.Integer(string="Week's first day number")
    mf_monday_quantity = fields.Float(string="Monday quantity")
    mf_tuesday_quantity = fields.Float(string="Tuesday quantity")
    mf_wednesday_quantity = fields.Float(string="Wednesday quantity")
    mf_thursday_quantity = fields.Float(string="Thursday quantity")
    mf_friday_quantity = fields.Float(string="Friday quantity")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def get_sale_order_lines_dates_list(self):
        quantities_by_week_day_number_list = [
            self.mf_monday_quantity,
            self.mf_tuesday_quantity,
            self.mf_wednesday_quantity,
            self.mf_thursday_quantity,
            self.mf_friday_quantity
        ]
        not_empty_sale_order_lines_dates_list = []
        for day_week_order, quantity in enumerate(quantities_by_week_day_number_list):
            if quantity:
                formatted_date = self._get_formatted_date(day_week_order)
                sale_order_dict, is_date_already_in_list = self._get_sale_order_dict_from_list_by_date(
                    not_empty_sale_order_lines_dates_list,
                    formatted_date
                )
                sale_order_dict["sale_order_lines"].append({
                    "product_id": self.mf_product_id.id,
                    "quantity": quantity
                })
                if not is_date_already_in_list:
                    not_empty_sale_order_lines_dates_list.append(sale_order_dict)
        return not_empty_sale_order_lines_dates_list

    def _get_formatted_date(self, day_week_order):
        year = int(str(self.mf_year_week)[:-2])
        month_number = self.mf_week_month
        day_number = self.mf_week_first_day_number + day_week_order
        first_day_weekday, month_days_number = monthrange(year, month_number)
        if day_number > month_days_number:
            day_number -= month_days_number
            month_number += 1
            if month_number > 12:
                year += 1
                month_number = 1
        year = str(year)
        month_number = str(month_number)
        day_number = str(day_number)
        if len(month_number) < 2:
            month_number = '0' + month_number
        if len(day_number) < 2:
            day_number = '0' + day_number
        return datetime.datetime.strptime(day_number + month_number + year, "%d%m%Y").strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _get_sale_order_dict_from_list_by_date(sale_order_lines_dates_list, date):
        for sale_order_lines_date_dict in sale_order_lines_dates_list:
            if sale_order_lines_date_dict["date"] == date:
                return sale_order_lines_date_dict, True
        return {
            "date": date,
            "sale_order_lines": []
        }, False
