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
    mf_bom_reference_ids = fields.One2many('mrp.bom', 'id', string='BoM', copy=True, ondelete='cascade')

    @api.model
    def default_get(self, fields_list):
        """
            Récupération des informations de l\'import
        """
        res = super(xml_import_bom_comparator, self).default_get(fields_list=fields_list)
        context = self.env.context
        if context.get('active_model', '') == 'xml.import.processing' and context.get('active_id', False):
            xml_import_processing_rs = self.env['xml.import.processing'].browse(context['active_id'])
            
            if xml_import_processing_rs:
                if not xml_import_processing_rs.processing_simulate_action_ids:
                    xml_import_processing_rs.simulate_file_analyse()

                res = self.__get_mrp_bom(res,xml_import_processing_rs.processing_simulate_action_ids) 

                res['mf_xml_import_id'] = xml_import_processing_rs.id

        return res


    def __get_mrp_bom(self, res, processing_simulate_action_ids):
        
        list_of_bom = []
        for id in self.processing_simulate_action_ids:
            if id.type != 'error' and id.object_model.model == 'mrp.bom':
                mrp_bom_if = self.env['mrp.bom'].search(['name','=',id.reference])
                if mrp_bom_if:
                    list_of_bom.append(mrp_bom_if.id)

        res['mf_bom_reference_ids'] = [(6, 0, list_of_bom)]

        return res

    @api.multi
    def validate_bom_selection(self):
        if self.mf_xml_import_id:
            self.mf_xml_import_id.mf_file_analyse(self.mf_xml_import_id.mf_get_file_content())