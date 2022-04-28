from openerp import models, fields, api, registry, _


class MFCalledSaleOrderGeneratorService(models.Model):
    _name = "mf.called.sale.order.generator.service"
    _description = "myfab generator service of called sales order"

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.one
    def generate_called_sales_order(self):
        called_sales_order_temp_ids = self.env["mf.called.sale.order.temp"].search()
        sales_order_to_generate = {}
        for called_sale_order_temp in called_sales_order_temp_ids:
            open_sale_order_name = called_sale_order_temp.sale_order_id.name
            new_sale_orders_dates = called_sale_order_temp.get_sale_order_lines_dates_dict()
            if open_sale_order_name in sales_order_to_generate:
                sales_order_to_generate[open_sale_order_name] = {
                    "sale_order_id": called_sale_order_temp,
                    "called_sale_orders": new_sale_orders_dates
                }
            else:
                self.merge_sale_order_lines_at_dates(
                    sales_order_to_generate[open_sale_order_name]["called_sale_orders"],
                    new_sale_orders_dates
                )

    def merge_sale_order_lines_at_dates(self, current_sale_order_lines, new_sale_order_lines):
        for new_date in list(new_sale_order_lines.keys()):
            if new_date in current_sale_order_lines:
                current_sale_order_lines[new_date].append(new_sale_order_lines[new_date])
