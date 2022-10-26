# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class xml_preprocessing_table_rule(models.Model):
    _inherit = "xml.preprocessing.table.rule"
    _order = 'sequence'

    #===========================================================================
    # COLUMN
    #===========================================================================
    #Modification parameter
    mf_use_old_value = fields.Boolean(string="Compare to old value", default=True)
    mf_modif_old_value = fields.Char(string="Old value")
    mf_result = fields.Char(string="Result", readonly=True, compute="_mf_compute_result")

    @api.one
    @api.onchange('action', 'new_name', 'add_all', 'add_list', 'attrib_name', 'attrib_value', 'remove_all', 'new_attrib_name', 'new_value', 'dst_path', 'move_create_copy', 'modif_attrib', 'modif_new_value', 'mf_use_old_value', 'mf_modif_old_value', 'beacon_to_concatenated', 'target_attribute', 'separator', 'new_name_concatenated', 'del_old_concatenate')
    def _mf_compute_result(self):
        result = ""

        if self.action == 'add':
            result = self._mf_get_string_value(self.new_name)
            if self.add_all:
                result += "\n" + _("with all children beacon")
            elif self.add_list and self.add_list != []:
                result += "\n" + _("with") + " " + self.add_list

        elif self.action == 'merge':
            result = _("Attribute") + " " + self._mf_get_string_value(self.attrib_name) + " = " + self._mf_get_string_value(self.attrib_value)
            if self.new_name:
                result += "\n" + _("In new beacon") + " " + self.new_name
        
        elif self.action =='remove':
            if self.remove_all:
                result = _("Delete all content")
        
        elif self.action =='rename':
            result = self._mf_get_string_value(self.new_name)
        
        elif self.action =='add_attrib':
            result = self._mf_get_string_value(self.new_attrib_name) + " = " + self._mf_get_string_value(self.new_value)
        
        elif self.action =='move':
            result = self._mf_get_string_value(self.dst_path)
            if self.move_create_copy:
                result += "\n" + _("With copy")
        
        elif self.action =='modification':
            result = self._mf_get_string_value(self.modif_attrib) + " = " + self._mf_get_string_value(self.modif_new_value)
            if self.mf_use_old_value:
                result += "\n" + _("If old value") + " = " + self._mf_get_string_value(self.mf_modif_old_value)  
        
        elif self.action =='concatenation':
            result = _("Beacon") + " " + self._mf_get_string_value(self.beacon_to_concatenated) + ", " + _("attribute") + " " + self._mf_get_string_value(self.target_attribute)
            if self.separator:
                result += " " + _("separated by") + " " + self.separator
            if self.new_name_concatenated:
                result += " " + _("in beacon") + " " + self.new_name_concatenated
            if self.del_old_concatenate:
                result += "\n" + _("Delete old beacon concatenated")

        self.mf_result = result

    @staticmethod
    def _mf_get_string_value(value):
        if not value:
            return ''
        else:
            return value