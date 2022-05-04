from openerp import models, fields, api, _
import csv
from StringIO import StringIO


class ParserServiceMF(models.TransientModel):
    _inherit = "parser.service.mf"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def get_records_from_file(
            self, file_extension, file_content, file_name, file_separator, file_quoting, file_encoding
    ):
        if file_extension == "csv_manitou":
            return self.get_records_from_csv_manitou(file_content, ';', '', file_encoding)
        else:
            return super(ParserServiceMF, self).get_records_from_file(
                file_extension, file_content, file_name, file_separator, file_quoting, file_encoding
            )

    def get_records_from_csv_manitou(self, file_content, file_separator, file_quoting, file_encoding):
        csv_rows = csv.reader(
            StringIO(file_content), delimiter=str(file_separator), quotechar=str(file_quoting) if file_quoting else None
        )
        called_sale_order_temp_to_create_list = []
        for csv_row_index, csv_row in enumerate(csv_rows):
            csv_row = [cell.decode(file_encoding).strip() for cell in csv_row]
            if csv_row_index == 0:
                continue
            product_ordered_id = self.env["product.product"].search([("code", '=', csv_row[3])], None, 1)
            sale_order_id = self.env["sale.order"].search([("name", '=', csv_row[5])], None, 1)
            called_sale_order_temp_to_create_list.append({
                "method": "create",
                "model": "mf.called.sale.order.temp",
                "fields": {
                    "mf_sale_order_id": sale_order_id.id,
                    "mf_product_id": product_ordered_id.id,
                    "mf_year_week": csv_row[42],
                    "mf_week_month": csv_row[43],
                    "mf_week_first_day_number": csv_row[44],
                    "mf_monday_quantity": csv_row[46],
                    "mf_tuesday_quantity": csv_row[48],
                    "mf_wednesday_quantity": csv_row[50],
                    "mf_thursday_quantity": csv_row[52],
                    "mf_friday_quantity": csv_row[54]
                },
                "rows": [{
                    "row_number": csv_row_index,
                    "row_content": csv_row
                }]
            })
        return called_sale_order_temp_to_create_list
