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
        new_file = False
        for file in self.mf_xml_import_processing_wizard_line_ids:
            file_extension = file.file_name.split(".")[-1].upper()
            if file_extension == "XML":
                new_file = {
                    "name":self.name,
                    "file":file.file,
                    "fname":file.file_name,
                    "preprocessing_file":False,
                    "prefname":False,
                    "preprocessing_id":self.mf_preprocessing_id.id,
                    "model_id":self.mf_configuration_table_id.id,
                }
            elif file_extension in ["XLSX","CSV"]:
                new_file = {
                    "name":self.name,
                    "mf_process_file_to_convert":file.file,
                    "mf_process_file_to_convert_name":file.file_name,
                    "file":False,
                    "fname":False,
                    "preprocessing_file":False,
                    "prefname":False,
                    "mf_process_conversion_id":self.mf_process_conversion_id.id,
                    "preprocessing_id":self.mf_preprocessing_id.id,
                    "model_id":self.mf_configuration_table_id.id,
                }
            new_processing = self.env['xml.import.processing'].create(new_file)
            if new_processing:
                new_processings.append(new_processing)
        self._mf_process(new_processings)

    def _mf_process(self, new_processings):
        for new_process in new_processings:
            new_process.preprocessing_xml_file()
            new_process.simulate_file_analyse()
            if not self.mf_stop_at_simulation:
                new_process.file_analyse()
            
