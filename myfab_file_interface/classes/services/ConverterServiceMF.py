from openerp import models, fields, api, _
import json
import csv
from StringIO import StringIO


class ConverterServiceMF(models.TransientModel):
    _name = "converter.service.mf"
    _description = "Converter service MyFab"

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
        return self.convert_models_list_to_csv(models_list, "\t", file_quoting, fields_names_list, file_encoding)

    def _convert_models_list_to_csv(self, models_list, file_separator, file_quoting, fields_names_list, file_encoding):
        csv_content = StringIO("")
        csv_writer = csv.writer(
            csv_content, delimiter=str(file_separator), quotechar=str(file_quoting), quoting=csv.QUOTE_ALL
        )
        csv_writer.writerow(fields_names_list)
        # TODO : in csv/txt we will export the first chosen model's records only
        records_list = models_list[0]["records"]
        self.write_records_list_in_csv(csv_writer, records_list, fields_names_list, file_encoding)
        return csv_content.getvalue()

    def write_records_list_in_csv(self, csv_writer, records_list, fields_names_list, file_encoding, prefix_field_name=""):
        for record_dict in records_list:
            self.write_record_dict_in_csv(csv_writer, record_dict, fields_names_list, file_encoding, prefix_field_name)

    def write_record_dict_in_csv(self, csv_writer, record_dict, fields_names_list, file_encoding, prefix_field_name):
        fields_to_write_dict = {}
        # TODO : the dicts values and lists' first element should be at the same level that the values
        # The first loop creates the "root" record (not any child record at this time)
        for field_name, field_value in record_dict.items():
            if type(field_value) not in [list, dict]:
                fields_to_write_dict[prefix_field_name + field_name] = field_value
        self.write_fields_dict_in_csv(csv_writer, fields_to_write_dict, fields_names_list, file_encoding)
        # The second loop creates the children records
        for field_name, field_value in record_dict.items():
            if type(field_value) is list:
                prefix_sub_field_name = self.get_prefix_for_field_name(field_name, prefix_field_name)
                self.write_records_list_in_csv(
                    csv_writer, field_value, fields_names_list, file_encoding, prefix_sub_field_name
                )
            elif type(field_value) is dict:
                prefix_sub_field_name = self.get_prefix_for_field_name(field_name, prefix_field_name)
                self.write_record_dict_in_csv(
                    csv_writer, field_value, fields_names_list, file_encoding, prefix_sub_field_name
                )

    @staticmethod
    def write_fields_dict_in_csv(csv_writer, fields_to_write_dict, fields_names_list, file_encoding):
        csv_row_to_write = []
        for field_name in fields_names_list:
            if field_name in fields_to_write_dict:
                field_value = fields_to_write_dict[field_name]
                cell_to_write = str(field_value) if type(field_value) is bool else field_value
            else:
                cell_to_write = ''
            csv_row_to_write.append(cell_to_write.encode(file_encoding))
        csv_writer.writerow(csv_row_to_write)

    @staticmethod
    def get_prefix_for_field_name(field_name, current_prefix):
        return current_prefix + '/' + field_name + '/' if current_prefix else field_name + '/'


