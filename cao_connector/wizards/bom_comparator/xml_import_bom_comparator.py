# -*- coding: utf-8 -*-
from openerp import models, fields, api

class xml_import_bom_comparator(models.TransientModel):
    """ 
        Wizard to create a bom comparator
    """
    _name = 'xml.import.bom.comparator'
    _description = 'Bom comparator'

     #===========================================================================
    # COLUMNS
    #===========================================================================

    mf_xml_import_id = fields.Many2one('xml.import.processing', string='Xml import processing')

    @api.model
    def default_get(self, fields_list):
        """
            Récupération des informations de l\'import
        """
        res = super(xml_import_bom_comparator, self).default_get(fields_list=fields_list)
        context = self.env.context
        if context.get('active_model', '') == 'xml.import.processing' and context.get('active_id', False):
            xml_import_processing_rs = self.env['xml.import.processing'].browse(context['active_id'])
            res['mf_xml_import_id'] = xml_import_processing_rs.id
                    
        return res

    @api.multi
    def validate_bom_selection(self):
        if self.mf_xml_import_id:
            lines = self.mf_xml_import_id.mf_get_file_content()
            self.mf_xml_import_id.mf_file_analyse(lines)