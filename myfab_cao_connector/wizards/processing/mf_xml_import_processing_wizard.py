# -*- coding: utf-8 -*-
from xml.dom import ValidationErr
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class mf_xml_import_processing_wizard(models.TransientModel):
    """ 
        wizard that create XML and XLSX processing dans launch them
    """
    _name = 'mf.xml.import.processing.wizard'

    name = fields.Char(required=True)
    mf_xml_import_processing_wizard_line_ids = fields.One2many('mf.xml.import.processing.wizard.line','mf_process_conversion_id', string='Files')
    mf_processing_id = fields.Many2one('xml.import.processing', string="Processing", default=lambda self: self._mf_compute_default_processing_id())
    mf_preprocessing_id = fields.Many2one('xml.preprocessing', string="PreProcessing")
    mf_process_conversion_id = fields.Many2one('mf.xlsx.convert.xml', string='XLSX/CSV Conversion')
    mf_configuration_table_id = fields.Many2one('xml.import.configuration.table', string='Configuration table', domain=[('state', '=', 'active')])
    mf_stop_at_simulation = fields.Boolean(string='Stop at simulation', default=lambda self: self._mf_compute_default_stop_at_simulation())

    @api.one
    @api.onchange('mf_processing_id')
    def _compute_mf_processing_id(self):
        self.write({
            'mf_process_conversion_id':self.mf_processing_id.mf_process_conversion_id.id,
            'mf_preprocessing_id':self.mf_processing_id.preprocessing_id.id,
            'mf_configuration_table_id':self.mf_processing_id.model_id.id,
        })

    # ===========================================================================
    # DEFAULT VALUE METHODS
    # ===========================================================================
    def _mf_default_configuration(self):
        return self.env['mf.modules.config'].search([], None, 1)

    def _mf_compute_default_processing_id(self):
        mf_config = self._mf_default_configuration()
        if mf_config:
            return mf_config.default_processing_wizard
        return False

    def _mf_compute_default_stop_at_simulation(self):
        mf_config = self._mf_default_configuration()
        if mf_config:
            return mf_config.default_stop_at_simulation
        return False

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.one
    def create_and_process(self):
        if self._mf_are_parameters_ok():
            files = []
            file_names_already_present = []
            for file in self.mf_xml_import_processing_wizard_line_ids:
                #TODO : s'assurer que le contenu du fichier est identique. Ne pas se baser que sur le nom
                if file.file_name and file.file_name not in file_names_already_present:
                    file_names_already_present.append(file.file_name)
                    files.append(file)
            self._mf_files_to_process(files)

    def _mf_are_parameters_ok(self):
        #TODO : check que le nom saisie n'est pas déjà existant
        if not self.mf_processing_id and not self.mf_configuration_table_id: 
            raise ValidationError(_("Select at least Processing or Configuration table."))
        for file in self.mf_xml_import_processing_wizard_line_ids:
            if file.file_name.split(".")[-1].upper() in ["XLSX","CSV"] and not self.mf_process_conversion_id:
                raise ValidationError(_("Select a XLSX/CSV Conversion."))
        return True

    def _mf_files_to_process(self, files):
        new_processings = []
        for file in files:
            new_processing = self._mf_create_process(file)
            if new_processing:
                new_processings.append(new_processing)
        self._mf_launch_processings(new_processings)

    def _mf_create_process(self, file_id):
        new_file = False
        new_processing = False

        file_extension = file_id.file_name.split(".")[-1].upper()
        if file_extension == "XML":
            new_file = {
                "file":file_id.file,
                "fname":file_id.file_name,
                "mf_process_file_to_convert":False,
                "mf_process_file_to_convert_name":False,
                "mf_process_conversion_id":False,
            }
        elif file_extension in ["XLSX","CSV"] and self.mf_process_conversion_id:
            new_file = {
                "file":False,
                "fname":False,
                "mf_process_file_to_convert":file_id.file,
                "mf_process_file_to_convert_name":file_id.file_name,
                "mf_process_conversion_id":self.mf_process_conversion_id.id,
            }
        if new_file and self.mf_configuration_table_id:
            new_file["name"] = self.name
            new_file["preprocessing_file"] = False
            new_file["prefname"] = False
            new_file["preprocessing_id"] = self.mf_preprocessing_id.id
            new_file["model_id"] = self.mf_configuration_table_id.id
            new_processing = self.env['xml.import.processing'].create(new_file)

        return new_processing

    def _mf_launch_processings(self, new_processings):
        for new_process in new_processings:
            new_process.preprocessing_xml_file()
            new_process.simulate_file_analyse()
            if not self.mf_stop_at_simulation:
                new_process.file_analyse()
            
