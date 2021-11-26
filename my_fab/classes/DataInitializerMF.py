# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, modules
import os
import logging

logger = logging.getLogger(__name__)
FIRST_FILE_TO_PROCESS_NAME = "ir.model.fields.csv"
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
        file_names = [f for f in os.listdir(data_dir_path) if os.path.isfile(os.path.join(data_dir_path, f))]
        # Sorting the list of files to process so we process the FIRST_FILE_TO_PROCESS_NAME in priority
        first_file_to_process_index = file_names.index(FIRST_FILE_TO_PROCESS_NAME)
        file_names.insert(0, file_names.pop(first_file_to_process_index))
        for file_name in file_names:
            self.process_file_by_model_name_in_file_name(file_name)

    # Process the file, depending on the imported model (in the file name)
    def process_file_by_model_name_in_file_name(self, file_name):
        parser_service = self.env["parser.service.mf"].create({})
        model_name = parser_service.get_model_name_from_file_name(file_name)
        if model_name in MODELS_TO_OVERWRITE_NAMES:
            # Delete all the MyFab current records for the model before importing
            myfab_default_records = self.env[model_name].search([("name", "=like", "MyFab - ")])
            myfab_default_records.unlink()
        self.import_file(parser_service, model_name, file_name)

    def import_file(self, parser_service, model_name, file_name):
        logger.info("Importing " + model_name)
        file = open(os.path.join(self.get_data_dir_path(), file_name), "rb")
        file_content = file.read()
        records_to_process_list = parser_service.get_records_from_csv(file_content, file_name, ',', '"', "utf-8")
        importer_service = self.env["importer.service.mf"].create({})
        importer_service.with_context(lang="fr_FR").import_records_list(records_to_process_list)
