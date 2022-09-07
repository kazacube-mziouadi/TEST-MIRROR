# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class mf_xml_import_processing_wizard_line(models.TransientModel):
    """ 
        Line of the wizard that create XML and XLSX processing dans launch them
    """
    _name = 'mf.xml.import.processing.wizard.line'

    mf_process_conversion_id = fields.Many2one('mf.xml.import.processing.wizard', string='Processing wizard')
    file_name =  fields.Char()
    file = fields.Binary()


