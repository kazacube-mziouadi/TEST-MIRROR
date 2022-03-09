# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, modules
import os
import logging
from openerp.tools import config

logger = logging.getLogger(__name__)
IMPORT_MODE_INSTALL = "install"
IMPORT_MODE_UPDATE = "update"


class DataInitializerMF(models.AbstractModel):
    _name = "data.initializer.mf"
    _auto = False

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    is_configuration_done = fields.Boolean(string="Is configuration done", default=False)

    # ===========================================================================
    # METHODS OVERRIDABLE
    # ===========================================================================

    # Method to override in order to declare models' names which data must be overwritten by the imported data files
    @staticmethod
    def get_models_to_overwrite_names():
        return []

    # Method to override in order to avoid importing models data by returning their names list
    @staticmethod
    def get_models_to_avoid_names():
        return []

    # Method to override in order to set configurations before initializing the data
    def set_configurations(self):
        pass

    # ===========================================================================
    # GENERAL METHODS
    # ===========================================================================
    @api.multi
    def launch_initialization(self):
        if "dev_mode_myfab" in config.options and config["dev_mode_myfab"]:
            return
        data_initializer = self.env[self._name].search([], None, 1)
        if not data_initializer or not data_initializer.is_configuration_done:
            self.set_configurations()
            self.import_data_files(IMPORT_MODE_INSTALL)
            self.env[self._name].create({
                "name": self._name,
                "is_configuration_done": True
            })
        self.import_data_files(IMPORT_MODE_UPDATE)
        self.unlink()

    def import_data_files(self, import_mode):
        data_dir_path = self.get_data_dir_path(import_mode)
        file_names = [file for file in os.listdir(data_dir_path) if os.path.isfile(os.path.join(data_dir_path, file))]
        parser_service = self.env["parser.service.mf"].create({})
        sorted(file_names, key=lambda file_name: self.env["file.mf"].get_sequence_from_file_name(file_name))
        importer_service = self.env["importer.service.mf"].create({})
        for file_name in file_names:
            self.process_file_by_model_name_in_file_name(import_mode, parser_service, importer_service, file_name)

    # Process the file, depending on the imported model (in the file name)
    def process_file_by_model_name_in_file_name(self, import_mode, parser_service, importer_service, file_name):
        model_name = self.env["file.mf"].get_model_name_from_file_name(file_name)
        if model_name in self.get_models_to_avoid_names():
            return
        if model_name in self.get_models_to_overwrite_names():
            # Delete all the MyFab current records for the model before importing
            myfab_default_records = self.env[model_name].search([("name", "=like", "MyFab - %")])
            myfab_default_records.unlink()
        self.import_file(import_mode, parser_service, importer_service, model_name, file_name)

    def import_file(self, import_mode, parser_service, importer_service, model_name, file_name):
        logger.info("Importing " + model_name)
        file = open(os.path.join(self.get_data_dir_path(import_mode), file_name), "rb")
        file_content = file.read()
        records_to_process_list = parser_service.get_records_from_csv(
            file_content, file_name, file_separator=',', file_quoting='"', file_encoding="utf-8"
        )
        importer_service.with_context(lang="fr_FR").import_records_list(records_to_process_list)

    @staticmethod
    # Returns the module's data directory
    def get_data_dir_path(import_mode):
        python_file_path = os.path.realpath(__file__)
        python_file_path_list = python_file_path.split(os.sep)
        module_directory_path = '/' + os.path.join(*python_file_path_list[:5])
        return os.path.join(module_directory_path, "static", "data", import_mode)
