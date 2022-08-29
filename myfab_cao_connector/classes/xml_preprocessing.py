# -*- coding: utf-8 -*-
from operator import truediv
from openerp import models, api, fields, _

MF_ATTRIB_SEP = ';;'
MF_VALUE_PROCESSING = '%PRE'

class xml_import_preprocessing(models.Model):
    _inherit = "xml.preprocessing"

    mf_preprocess_xlsx_conversion_id = fields.Many2one('mf.xlsx.convert.xml', string='XLSX Conversion', ondelete='set null')
    mf_preprocess_xlsx_file = fields.Binary(string="XLSX file to convert")
    mf_preprocess_xlsx_file_name = fields.Char()
    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.one
    def mf_xlsx_conversion(self):
        """
        Use xlsx conversion objet for create xlsx file and write file in preprocessing object.
        """ 
        if not self.mf_preprocess_xlsx_conversion_id:
            return True
        if not self.mf_preprocess_xlsx_file:
            return False

        self.mf_preprocess_xlsx_conversion_id.write({'xlsx_file':self.mf_preprocess_xlsx_file, 
                                                    'xlsx_file_name':self.mf_preprocess_xlsx_file_name,
                                                    })
                        
        conversion_ok = self.mf_preprocess_xlsx_conversion_id.mf_convert()
        conversion_ok = conversion_ok[0]

        if conversion_ok:
            self.write({'file': self.mf_preprocess_xlsx_conversion_id.xml_file, 
                        'fname': self.mf_preprocess_xlsx_conversion_id.xml_file_name,
                        'message': self.mf_preprocess_xlsx_conversion_id.execution_message,
                        })
        else:
            self.message = self.mf_preprocess_xlsx_conversion_id.execution_message

        return conversion_ok

    @api.one
    def pre_processing_xml_file(self):
        if self.mf_preprocess_xlsx_conversion_id and self.mf_preprocess_xlsx_file:
            self.mf_xlsx_conversion()

        if self.file:
            super(xml_import_preprocessing, self).pre_processing_xml_file()

    #Overwriting the method
    def action_write(self, parent, element, rule_rc):
        # We don't do super, because we replace the existing method
        #res = super(xml_import_preprocessing, self).action_write(parent, element, rule_rc)

        # Copy and optimization of the existing code
        dict_value = {}
        new_value_list = []
        old_value_list = []

        attrib_list = rule_rc.modif_attrib.split(MF_ATTRIB_SEP)
        need_processing_value = (len(rule_rc.modif_new_value) > len(MF_VALUE_PROCESSING) and rule_rc.modif_new_value[:len(MF_VALUE_PROCESSING)] == MF_VALUE_PROCESSING)
        if rule_rc.modif_new_value:
            new_value_list = eval(rule_rc.modif_new_value[len(MF_VALUE_PROCESSING):]) if need_processing_value else rule_rc.modif_new_value.split(MF_ATTRIB_SEP)
        if rule_rc.mf_modif_old_value:
            old_value_list = rule_rc.mf_modif_old_value.split(MF_ATTRIB_SEP)

        cpt = 0
        for attrib in attrib_list:
            dict_value[attrib] = self._mf_get_new_value(element.get(attrib), need_processing_value, cpt, new_value_list, rule_rc.mf_use_old_value, old_value_list)            
            cpt += 1
        #Add value to element
        cpt += 1
        # remove create copy option
#         if rule_rc.write_create_copy:
#             new_ele = lxml.etree.SubElement(parent, element.tag)
#             for attrib in element.keys():
#                 if attrib in dict_value:
#                     new_ele.set(attrib, dict_value[attrib])
#                 else:
#                     new_ele.set(rule_rc.modif_attrib, element.get(attrib))
#                     
#             res = new_ele
#         else:

        for attrib in dict_value:
            element.set(attrib, dict_value[attrib])
            
        res=False
        return res


    def _mf_get_new_value(self, current_value, need_processing_value, index, new_values, use_old_values, old_values):
        
        # copy the current value in the final value in case of any changes possible, to not modify the current value
        final_value = current_value

        old_value = old_values[index] if len(old_values) > index else ''
        new_value = new_values[index] if len(new_values) > index else ''

        # Only old value corresponding to the current value
        if not use_old_values or str(final_value).strip() == str(old_value).strip():
            if not need_processing_value:
                final_value = new_value
            else:
                eval_value = final_value #evaluated value : variable referenced in code by string
                for fact in new_value:
                    if fact[0] == '+':
                        final_value += fact[1:]
                    else:
                        final_value += eval('eval_value['+fact+']')

        return final_value