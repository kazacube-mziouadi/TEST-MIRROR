from openerp import models, fields, api, _
import json
import datetime
import os
import base64


class MyFabInterfaceMF(models.AbstractModel):
    _name = "myfab.interface.mf"
    _auto = False
    _description = "MyFab interface abstract - To use it add to the inheriter model a model_dictionaries_to_export_mf " \
                   "One2many field targeting a model inheriting from model.dictionary.mf"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def format_models_to_export_to_dict(self):
        content_dict = {}
        for model_dictionary in self.model_dictionaries_to_export_mf:
            model_list_name = model_dictionary.model_to_export_mf.model + 's'
            content_dict[model_list_name] = model_dictionary.get_dict_of_objects_to_export()
        return content_dict
