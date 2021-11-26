from openerp import models, fields, api, _
import simplejson
import csv
from StringIO import StringIO
from openerp.exceptions import MissingError


class ExporterServiceMF(models.TransientModel):
    _name = "exporter.service.mf"
    _description = "Exporter service MyFab"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @staticmethod
    def format_models_to_export_to_dict(model_dictionaries_to_export_mf):
        content_dict = []
        for model_dictionary in model_dictionaries_to_export_mf:
            model_name = model_dictionary.model_to_export_mf.model
            content_dict.append({
                "model": model_name,
                "records": model_dictionary.get_list_of_records_to_export()
            })
        return content_dict

    def format_models_to_import_to_dict(self, model_dictionaries_to_import_mf):
        selected_models_dict = self.format_models_to_export_to_dict(model_dictionaries_to_import_mf)
        json_content_array = []
        for model_object in selected_models_dict:
            model_name = model_object["model"]
            for record_dict in model_object["records"]:
                json_content_array.append({
                    "method": "create",
                    "model": model_name,
                    "fields": record_dict
                })
        return json_content_array
