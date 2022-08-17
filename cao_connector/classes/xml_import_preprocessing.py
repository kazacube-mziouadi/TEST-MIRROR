# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class xml_import_preprocessing(models.Model):
    _inherit = "xml.preprocessing"

    #Overwriting the method
    def action_write(self, parent, element, rule_rc):
        #We don't do super, because we replace the existing method
        #res = super(xml_import_preprocessing, self).action_write(parent, element, rule_rc)

        #Copy and optimization of the existing code
        value = ''
        dict_value = {}
        attrib_list = rule_rc.modif_attrib.split(';;')
        new_value_list = rule_rc.modif_new_value.split(';;')
        old_value_list = rule_rc.mf_modif_old_value.split(';;')
        cpt = 0

        #Processing values       
        if len(rule_rc.modif_new_value) > 4 and rule_rc.modif_new_value[:4] == '%PRE':
            res = eval(rule_rc.modif_new_value[4:])
            for attrib in attrib_list:
                value = element.get(attrib)
                # No old value defined or corresponding to the current value
                if len(rule_rc.mf_modif_old_value) <= 0 or value == old_value_list[cpt]:
                    ele_value = value
                    cur = res[cpt]
                    for fact in cur:
                        if fact[0] == '+':
                            value = value + fact[1:]
                        else:    
                            to_eval = 'ele_value['
                            to_eval = to_eval+fact+']'
                            value = value + eval(to_eval)
                            
                dict_value[attrib] = value
                value=''
                cpt += 1
        else:
            for attrib in attrib_list:
                value = element.get(attrib)
                # No old value defined or corresponding to the current value
                if len(rule_rc.mf_modif_old_value) <= 0 or element.get(attrib) == old_value_list[cpt]:
                    value = new_value_list[cpt]
                dict_value[attrib] = value
                value=''
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