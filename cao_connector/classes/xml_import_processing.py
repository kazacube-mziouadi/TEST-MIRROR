# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError, ValidationError

class xml_import_processing(models.Model):
    _inherit = 'xml.import.processing'   

    @api.multi
    def file_analyse(self):
        super(xml_import_processing, self).file_analyse()

        is_need_bom_comparator = False

        for element in self.processing_records_ids:
            if element.type != 'error':
                if element.object_model.model == 'mrp.bom.temporary':
                    is_need_bom_comparator = True
                if element.object_model.model in ('mrp.bom.temporary','product.product.temporary'):
                    element.reference.mf_xml_import_processing_id = element.id
                
        if is_need_bom_comparator:
            return self.__open_bom_comparator_wizard() 
        else:       
            return False

    def delete_elements_temporary(self):
        for element in self.processing_records_ids:
            if element.type != 'error':
                if element.object_model.model in ('mrp.bom.temporary','product.product.temporary'):
                    element.reference.unlink()

    def __open_bom_comparator_wizard(self):
        return {
            "name": _("BoM comparator"),
            "view_mode": "form",
            "res_model": "xml.import.bom.comparator",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {
                "mf_xml_import_id": self.id,
            }
        }

    





