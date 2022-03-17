from openerp import models, fields, api, _


class ExporterServiceMF(models.TransientModel):
    _name = "exporter.service.mf"
    _description = "Exporter service MyFab"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @staticmethod
    def get_records_to_export_list_from_model_dictionary(model_dictionary):
        records_list = []
        model_name = model_dictionary.model_to_export_mf.model
        records_to_export_list = model_dictionary.get_list_of_records_to_export()
        for record_to_export in records_to_export_list:
            records_list.append({
                "method": "create",
                "model": model_name,
                "fields": record_to_export
            })
        return records_list
