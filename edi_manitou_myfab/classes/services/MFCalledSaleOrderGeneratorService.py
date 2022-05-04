from openerp import models, fields, api, registry, _


class MFCalledSaleOrderGeneratorService(models.TransientModel):
    _name = "mf.called.sale.order.generator.service"
    _description = "myfab generator service of called sales order"

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def generate_called_sales_order(self):
        called_sales_order_temp_ids = self.env["mf.called.sale.order.temp"].search([])
        # TODO (IS-132) : Refondre la structure list/dict Python en objets Python
        """
        The below structure will be created : 
        
        open_sales_order_to_generate = [
            {
                "sale_order_id": sale.order(2),
                "called_sale_orders": [
                    {
                        "date":"01-02-2022",       	
                        "sale_order_lines": [
                            {
                                "product_id": product.product(56),
                                "quantity": 75
                            }
                        ]
                    }
                ]
            }
        ]
        """
        open_sales_order_to_generate = []
        for called_sale_order_temp in called_sales_order_temp_ids:
            new_sale_orders_dates = called_sale_order_temp.get_sale_order_lines_dates_list()
            sale_order_id = called_sale_order_temp.mf_sale_order_id
            open_sale_order_dict = self._get_open_sale_order_in_list_by_id(
                open_sales_order_to_generate,
                sale_order_id.id
            )
            if open_sale_order_dict:
                self._merge_called_sales_order_list(open_sale_order_dict["called_sale_orders"], new_sale_orders_dates)
            else:
                open_sales_order_to_generate.append({
                    "sale_order_id": sale_order_id.id,
                    "called_sale_orders": new_sale_orders_dates
                })
        self._generate_called_sales_order_from_temp_list(open_sales_order_to_generate)
        called_sales_order_temp_ids.unlink()

    @staticmethod
    def _get_open_sale_order_in_list_by_id(open_sales_order_list, sale_order_id):
        for sale_order_to_generate in open_sales_order_list:
            if sale_order_to_generate["sale_order_id"] == sale_order_id:
                return sale_order_to_generate
        return None

    @staticmethod
    def _merge_called_sales_order_list(current_sale_orders, new_sale_orders):
        for new_sale_order in new_sale_orders:
            new_sale_order_merged = False
            for current_sale_order in current_sale_orders:
                if current_sale_order["date"] == new_sale_order["date"]:
                    current_sale_order["sale_order_lines"] += new_sale_order["sale_order_lines"]
                    new_sale_order_merged = True
            if not new_sale_order_merged:
                current_sale_orders.append(new_sale_order)

    def _generate_called_sales_order_from_temp_list(self, sales_order_temp_list):
        for open_sale_order_dict in sales_order_temp_list:
            self._generate_called_sale_order_for_open_sale_order_dict(open_sale_order_dict)

    def _generate_called_sale_order_for_open_sale_order_dict(self, open_sale_order_dict):
        for called_sale_order_temp_dict in open_sale_order_dict["called_sale_orders"]:
            generate_called_sale_order_wizard = self.env["generate.called.sale.order"].create({
                "sale_id": open_sale_order_dict["sale_order_id"],
                "date": called_sale_order_temp_dict["date"],
                "called_order_line_ids": self._get_sale_order_lines_create_dicts_list(
                    open_sale_order_dict["sale_order_id"],
                    called_sale_order_temp_dict["sale_order_lines"]
                )
            })
            generate_called_sale_order_wizard.generate_called_order()

    def _get_sale_order_lines_create_dicts_list(self, sale_order_id, sale_order_lines_list):
        sale_order_lines_create_dicts_list = []
        for sale_order_line_dict in sale_order_lines_list:
            sale_order_line_id = self.env["sale.order.line"].search([
                ("sale_order_id", '=', sale_order_id), ("product_id", '=', sale_order_line_dict["product_id"])
            ], None, 1)
            sale_order_line_dict.update({
                "sale_order_line_id": sale_order_line_id.id,
                "price": sale_order_line_id.price_unit,
            })
            sale_order_lines_create_dicts_list.append((0, 0, sale_order_line_dict))
        return sale_order_lines_create_dicts_list
