# -*- coding: utf-8 -*-
from abc import abstractmethod
from openerp import models, fields, api, _, modules
import os
import logging

logger = logging.getLogger(__name__)
MODELS_TO_OVERWRITE_NAMES = ["excel.import"]


class DataInitializerMF(models.AbstractModel):
    _name = "data.initializer.mf"
    _auto = False

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)

    @staticmethod
    # Returns the module's data directory
    def get_data_dir_path():
        python_file_path = os.path.realpath(__file__)
        python_file_path_list = python_file_path.split(os.sep)
        module_directory_path = '/' + os.path.join(*python_file_path_list[:5])
        return os.path.join(module_directory_path, "static", "data")

    @api.multi
    def import_files(self):
        data_dir_path = self.get_data_dir_path()
        files = [f for f in os.listdir(data_dir_path) if os.path.isfile(os.path.join(data_dir_path, f))]
        for file_name in files:
            self.process_file(file_name)

    # Process the file, depending on the imported model
    def process_file(self, file_name):
        model_name = self.get_model_name_from_file_name(file_name)
        if model_name in MODELS_TO_OVERWRITE_NAMES:
            # Delete all the MyFab current records for the model before importing
            myfab_default_records = self.env[model_name].search([("name", "like", "MyFab - ")])
            myfab_default_records.unlink()
        else:
            # Import only when no record for model
            existing_records = self.env[model_name].search([])
            if existing_records:
                return
        self.import_file_data(model_name, file_name)

    @staticmethod
    # Returns the model name from a given import file name (the file name without the extension)
    def get_model_name_from_file_name(file_name):
        file_name_split = file_name.split('.')
        file_name_split.pop()
        return '.'.join(file_name_split)

    def import_file_data(self, model_name, file_name):
        logger.info("Importing " + model_name)
        file = open(os.path.join(self.get_data_dir_path(), file_name), "r")
        file_content = file.read()
        base_import = self.env["base_import.import"].create({
            "res_model": model_name,
            "file_type": "text/csv",
            "file_name": file_name,
            "file": file_content
        })
        parse_result = base_import.parse_preview(
            options={"headers": True, "separator": ',', "quoting": '"'},
            count=1
        )
        base_import.with_context(lang="fr_FR").do(
            fields=parse_result[0]["headers"],
            options={"headers": True, "separator": ',', "quoting": '"'}
        )
