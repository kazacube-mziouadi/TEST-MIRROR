# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

MF_ATTRIB_SEP = ';;'
MF_VALUE_PROCESSING = '%PRE'

class xml_import_preprocessing(models.Model):
    _inherit = "xml.preprocessing"

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