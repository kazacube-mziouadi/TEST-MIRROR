from openerp import models, fields, api, _


class ExporterServiceMF(models.TransientModel):
    _name = "exporter.service.mf"
    _description = "Exporter service MyFab"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def get_records_to_export_list_from_model_dictionary(self, model_dictionary, method_to_apply):
        records_list = []
        records_to_export_list = model_dictionary.get_list_of_records_to_export()
        for record_to_export in records_to_export_list:
            records_list.append(self.get_record_to_export_dict(record_to_export, model_dictionary, method_to_apply))
        return records_list

    def get_record_to_export_dict(self, record_to_export, model_dictionary, method_to_apply):
        model_name = model_dictionary.model_to_export_mf.model
        record_to_export_dict = {
            "method": method_to_apply,
            "model": model_name
        }
        if method_to_apply in ["create", "delete", "search"]:
            record_to_export_dict["fields"] = record_to_export
        elif method_to_apply in ["write", "merge"]:
            record_to_export_dict.update({
                "fields": self.get_fields_to_search_dict(record_to_export, model_dictionary),
                "fields_to_write": record_to_export
            })
        else:
            raise ValueError("The " + method_to_apply + " method to apply is not supported.")
        return record_to_export_dict

    def get_fields_to_search_dict(self, record_to_export, model_dictionary):
        fields_to_search_dict = {}
        for field_to_search in model_dictionary.mf_fields_to_search:
            if field_to_search in model_dictionary.fields_to_export_mf:
                fields_to_search_dict[field_to_search.name] = record_to_export[field_to_search.name]
        for field_to_export in model_dictionary.fields_to_export_mf:
            for child_model_dictionary in model_dictionary.children_model_dictionaries_mf:
                if child_model_dictionary.model_to_export_mf.model == field_to_export.relation:
                    if type(record_to_export[field_to_export.name]) is list:
                        child_fields_to_search = []
                        for sub_record_to_export in record_to_export[field_to_export.name]:
                            sub_record_fields_to_search = self.get_fields_to_search_dict(
                                sub_record_to_export, child_model_dictionary
                            )
                            if sub_record_fields_to_search:
                                child_fields_to_search.append(sub_record_fields_to_search)
                    else:
                        child_fields_to_search = self.get_fields_to_search_dict(
                            record_to_export[field_to_export.name], child_model_dictionary
                        )
                    if child_fields_to_search:
                        fields_to_search_dict[field_to_export.name] = child_fields_to_search
        return fields_to_search_dict
