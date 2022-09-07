# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class mf_xml_import_processing_wizard(models.TransientModel):
    """ 
        wizard that create XML and XLSX processing dans launch them
    """
    _name = 'mf.xml.import.processing.wizard'

    @api.one
    @api.onchange('mf_processing_id')
    def _compute_mf_processing_id(self):
        self.mf_process_conversion_id = self.mf_processing_id.mf_process_conversion_id
        self.mf_preprocessing_id = self.mf_processing_id.preprocessing_id
        self.mf_configuration_table_id = self.mf_processing_id.model_id

    name = fields.Char(required=True)
    mf_xml_import_processing_wizard_line_ids = fields.One2many('mf.xml.import.processing.wizard.line','mf_process_conversion_id', string='Processing wizard lines')
    mf_processing_id = fields.Many2one('xml.import.processing', string="Processing")
    mf_preprocessing_id = fields.Many2one('xml.preprocessing', string="PreProcessing")
    mf_process_conversion_id = fields.Many2one('mf.xlsx.convert.xml', string='XLSX/CSV Conversion')
    mf_configuration_table_id = fields.Many2one('xml.import.configuration.table', string='Configuration table', domain=[('state', '=', 'active')])
    mf_stop_at_simulation = fields.Boolean(string='Stop at simulation')


    @api.multi
    def create_and_process(self):
        new_processings = []
        for file in self.mf_xml_import_processing_wizard_line_ids:
            new_processing = self._mf_create_process(file,len(new_processings))
            if new_processing:
                new_processings.append(new_processing)
        self._mf_process(new_processings)

    def _mf_create_process(self, file_id, index):
        new_file = False
        new_processing = False

        file_extension = file_id.file_name.split(".")[-1].upper()
        if file_extension == "XML":
            new_file = {
                "file":file_id.file,
                "fname":file_id.file_name,
            }
        elif file_extension in ["XLSX","CSV"] and self.mf_process_conversion_id:
            new_file = {
                "file":False,
                "fname":False,
                "mf_process_file_to_convert":file_id.file,
                "mf_process_file_to_convert_name":file_id.file_name,
                "mf_process_conversion_id":self.mf_process_conversion_id.id,
            }
        if new_file:
            new_file["name"] = self.name + ' ' + file_id.file_name + ((' ' + str(index)) if index > 0 else '')
            new_file["preprocessing_file"] = False
            new_file["prefname"] = False
            new_file["preprocessing_id"] = self.mf_preprocessing_id.id
            new_file["model_id"] = self.mf_configuration_table_id.id
            new_processing = self.env['xml.import.processing'].create(new_file)

        return new_processing

    def _mf_process(self, new_processings):
        for new_process in new_processings:
            new_process.preprocessing_xml_file()
            new_process.simulate_file_analyse()
            if not self.mf_stop_at_simulation:
                new_process.file_analyse()
            
