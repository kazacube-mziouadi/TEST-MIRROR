from openerp import models, fields, api, _
import json
import csv
from StringIO import StringIO


class ConverterServiceMF(models.TransientModel):
    _name = "converter.service.mf"
    _description = "Converter service myfab"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def convert_models_list_to_file_content(self, models_list, file_extension, file_separator, file_quoting,
                                            fields_names_list, file_encoding="utf-8"):
        if file_extension == "json":
            return self._convert_models_list_to_json(models_list)
        elif file_extension == "csv":
            return self._convert_models_list_to_csv(
                models_list, file_separator, file_quoting, fields_names_list, file_encoding
            )
        elif file_extension == "txt":
            return self._convert_models_list_to_txt(models_list, file_quoting, fields_names_list, file_encoding)
        raise ValueError("The " + file_extension + " file extension is not supported.")

    @staticmethod
    def _convert_models_list_to_json(models_list):
        return json.dumps(models_list, sort_keys=True, indent=4)

    def _convert_models_list_to_txt(self, models_list, file_quoting, fields_names_list, file_encoding):
        return self._convert_models_list_to_csv(models_list, "\t", file_quoting, fields_names_list, file_encoding)

    def _convert_models_list_to_csv(self, models_list, file_separator, file_quoting, fields_names_list, file_encoding):
        csv_content = StringIO("")
        csv_writer = csv.writer(
            csv_content, delimiter=str(file_separator), quotechar=str(file_quoting) if file_quoting else None,
            quoting=csv.QUOTE_ALL if file_quoting else csv.QUOTE_NONE
        )
        csv_writer.writerow(fields_names_list)
        records_list = self.get_records_list_from_models_list(models_list)
        rows_to_write_list = self.get_records_rows_to_write(records_list, fields_names_list, file_encoding)
        for row_to_write in rows_to_write_list:
            csv_writer.writerow(row_to_write)
        return csv_content.getvalue()

    @staticmethod
    def get_records_list_from_models_list(models_list):
        records_list = []
        first_model_name = None
        for model_dict in models_list:
            if not first_model_name:
                first_model_name = model_dict["model"]
            if first_model_name == model_dict["model"]:
                records_list.append(model_dict["fields"])
        return records_list

    def get_records_rows_to_write(self, records_list, fields_names_list, file_encoding, prefix_field_name=""):
        rows_list = []
        for record_dict in records_list:
            record_rows_list = self.get_record_rows_to_write(
                record_dict, fields_names_list, file_encoding, prefix_field_name
            )
            rows_list = rows_list + record_rows_list
        return rows_list

    def get_record_rows_to_write(self, record_dict, fields_names_list, file_encoding, prefix_field_name):
        # Dict containing the not relational fields name and corresponding value for the processed record
        # ex : { name: "John", ... }
        fields_to_write_dict = {}
        rows_list = []
        # The first loop creates the "root" record (not any child record at this time)
        for field_name, field_value in record_dict.items():
            if type(field_value) not in [list, dict]:
                fields_to_write_dict[prefix_field_name + field_name] = field_value
        rows_list.append(
            self.get_record_row_to_write_from_fields_dict(fields_to_write_dict, fields_names_list, file_encoding)
        )
        # The second loop creates the children records
        for field_name, field_value in record_dict.items():
            if field_value and type(field_value) in [dict, list]:
                prefix_sub_field_name = self.get_prefix_for_field_name(field_name, prefix_field_name)
                if type(field_value) is dict:
                    relation_field_rows_list = self.get_record_rows_to_write(
                        field_value, fields_names_list, file_encoding, prefix_sub_field_name
                    )
                else:
                    relation_field_rows_list = self.get_records_rows_to_write(
                        field_value, fields_names_list, file_encoding, prefix_sub_field_name
                    )
                # We make sure the first element of the relation field's list is on the same row than the root element
                rows_list[0] = self.merge_cells_list(rows_list[0], relation_field_rows_list[0])
                # Then we add the rest of the relation field's list on separate rows
                rows_list = rows_list + relation_field_rows_list[1:]
        return rows_list

    @staticmethod
    def get_record_row_to_write_from_fields_dict(fields_to_write_dict, fields_names_list, file_encoding):
        row_to_write = []
        for field_name in fields_names_list:
            if field_name in fields_to_write_dict:
                field_value = fields_to_write_dict[field_name]
                cell_to_write = str(field_value) if type(field_value) in [bool, int, float] else field_value
            else:
                cell_to_write = ''
            row_to_write.append(cell_to_write.encode(file_encoding))
        return row_to_write

    @staticmethod
    def merge_cells_list(cells_list1, cells_list2):
        for cell_index, row2_cell in enumerate(cells_list2):
            if row2_cell != "":
                cells_list1[cell_index] = row2_cell
        return cells_list1

    @staticmethod
    def get_prefix_for_field_name(field_name, current_prefix):
        return current_prefix + field_name + '/' if current_prefix else field_name + '/'
