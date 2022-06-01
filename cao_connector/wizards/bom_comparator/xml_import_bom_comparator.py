# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError, ValidationError

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
    mf_bom_reference_ids = fields.One2many('mrp.bom', 'id', string='BoM', ondelete='cascade')
    mf_bom_temporary_reference_ids = fields.One2many('mrp.bom.temporary', 'id', string='BoM', ondelete='cascade')

    @api.model
    def default_get(self, fields_list):
        """
            Récupération des informations de l\'import
        """
        res = super(xml_import_bom_comparator, self).default_get(fields_list=fields_list)
        context = self.env.context
        if context.get('mf_xml_import_id', False):
            xml_import_processing_rs = self.env['xml.import.processing'].browse(context['mf_xml_import_id'])
            
            if xml_import_processing_rs:
                res = self.__get_mrp_bom(res,xml_import_processing_rs.processing_records_ids) 
                res['mf_xml_import_id'] = xml_import_processing_rs.id

        return res

    def __get_mrp_bom(self, res, processing_records_ids):
        list_of_bom = []
        for id in processing_records_ids:
            if id.type != 'error' and id.reference and len(id.reference) > 0 and id.object_model.model == 'mrp.bom.temporary':
                mrp_bom_rc = self.env['mrp.bom'].search([('product_id','=',id.reference.id)])
                if mrp_bom_rc:
                    list_of_bom.append(mrp_bom_rc.id)

        res['mf_bom_reference_ids'] = [(6, 0, list_of_bom)]

        return res

    @api.multi
    def validate_bom_selection(self):
        self.mf_xml_import_id = False
        self.mf_bom_reference_ids = False
        self.mf_xml_import_id.delete_elements_temporary()