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
                models_list, file_separator, file_quoting, file_encoding, fields_names_list
            )
        elif file_extension == "txt":
            return self._convert_models_list_to_txt(models_list, file_quoting, file_encoding, fields_names_list)
        raise ValueError("The " + file_extension + " file extension is not supported.")

    @staticmethod
    def _convert_models_list_to_json(models_list):
        return json.dumps(models_list, sort_keys=True, indent=4)

    def _convert_models_list_to_txt(self, models_list, file_quoting, file_encoding, fields_names_list):
        return self.convert_models_list_to_csv(models_list, "\t", file_quoting, file_encoding)

    def _convert_models_list_to_csv(self, models_list, file_separator, file_quoting, file_encoding, fields_names_list):
        csv_content = StringIO("")
        csv_writer = csv.writer(
            csv_content, delimiter=str(file_separator), quotechar=str(file_quoting), quoting=csv.QUOTE_ALL
        )
        csv_writer.writerow(fields_names_list)
        # TODO : en csv/txt on exportera les enregistrements du premier modele choisi uniquement
        records_list = models_list[0]["records"]
        self.write_records_list_in_csv(csv_writer, records_list)
        return ""

    def write_records_list_in_csv(self, csv_writer, records_list, prefix_field_name=""):
        for record_dict in records_list:
            self.write_records_list_in_csv(csv_writer, record_dict, prefix_field_name)

    def write_record_dict_in_csv(self, csv_writer, record_dict, prefix_field_name):
        for field_name, field_value in record_dict.items():
            if type(field_value) is list:
                prefix_sub_field_name = self.get_prefix_for_field_name(field_name, prefix_field_name)
                self.write_records_list_in_csv(csv_writer, field_value, prefix_sub_field_name)
            elif type(field_value) is dict:
                prefix_sub_field_name = self.get_prefix_for_field_name(field_name, prefix_field_name)
                self.write_record_dict_in_csv(csv_writer, field_value, prefix_sub_field_name)
            else:
                # TODO : on ne veut ecrire qu'une ligne dans le CSV pour tout un dictionnaire parcouru !
                pass

    @staticmethod
    def get_prefix_for_field_name(field_name, current_prefix):
        if current_prefix:
            return current_prefix + '/' + field_name + '/'
        else:
            return field_name + '/'


