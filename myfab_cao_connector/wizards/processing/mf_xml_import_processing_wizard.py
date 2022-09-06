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
    _description = 'Splitting of a sale'

    name = fields.Char(string='Name', required=True)
    mf_xml_import_processing_wizard_line_ids = fields.One2many('mf.xml.import.processing.wizard.line', string='XLSX Conversion')
    mf_processing_id = fields.Many2one('xml.import.processing', string="Processing")
    mf_process_xlsx_conversion_id = fields.Many2one('mf.xlsx.convert.xml', string='XLSX Conversion')
    mf_preprocessing_id = fields.Many2one('xml.preprocessing', string="Pre-treatment")
    mf_configuration_table_id = fields.Many2one('xml.import.configuration.table', string='Configuration table', domain=[('state', '=', 'active')])
    mf_stop_at_preprocessing = fields.Boolean(string='Stop at preprocessing')

    def create_and_process(self):
        new_processings = []
        new_file = False
        for file in self.mf_xml_import_processing_wizard_line_ids:
            if file.fname.split(".")[-1] == "xml":
                new_file = {
                    "file":file.file,
                    "preprocessing_id":self.mf_preprocessing_id,
                    "model_id":self.mf_configuration_table_id,
                }
            elif file.fname.split(".")[-1] in ["xlsx","xls"]:
                new_file = {
                    "mf_process_xlsx_file":file.file,
                    "mf_process_xlsx_conversion_id":self.mf_process_xlsx_conversion_id,
                    "preprocessing_id":self.mf_preprocessing_id,
                    "model_id":self.mf_configuration_table_id,
                }
            if self.mf_processing_id:
                temp_processing = self.mf_processing_id.copy()
                new_processing = temp_processing.write(new_file)
                new_processings.push(new_processing)
            else:
                new_processing = self.env['xml.import.processing'].create(new_file)
                new_processings.push(new_processing)
        for new_process in new_processings:
            if new_process.mf_process_xlsx_file:
                new_process.mf_xlsx_conversion()
            new_process.preprocessing_xml_file()
            new_process.simulate_file_analyse()
            if not self.mf_stop_at_preprocessing:
                new_process.file_analyse()
            
