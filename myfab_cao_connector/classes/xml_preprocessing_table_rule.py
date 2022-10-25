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
    def _mf_compute_result(self):
        result = ""

        if self.action == 'add':
            result = self.new_name
            if self.add_all:
                result += "\n" + _("with all children beacon")
            elif self.add_list != []:
                result += "\n" + _("with") + " " + self.add_list
        elif self.action == 'merge':
            result = _("Attribute") + " " + self.attrib_name + " = " + self.attrib_value
            if self.new_name:
                result += "\n" + _("In new beacon") + " " + self.new_name
        elif self.action =='remove':
            result = _("Delete content") + " : " + self.remove_all
        elif self.action =='rename':
            result = self.new_name
        elif self.action =='add_attrib':
            result = self.new_attrib_name + " = " + self.new_value
        elif self.action =='move':
            result = self.dst_path
            if self.move_create_copy:
                result += "\n" + _("With copy")
        elif self.action =='modification':
            result = self.modif_attrib + " = " + self.modif_new_value
            if self.mf_use_old_value:
                result += "\n" + _("If old value") + " = " + self.mf_modif_old_value  
        elif self.action =='concatenation':
            result = _("Beacon") + " " + self.beacon_to_concatenated + ", " + _("attribute") + " " + self.target_attribute 
            if self.separator:
                result += " " + _("separated by") + " " + self.separator
            if self.new_name_concatenated:
                result += " " + _("in beacon") + " " + self.new_name_concatenated
            if self.del_old_concatenate:
                result += "\n" + _("Delete old beacon concatenated")

        self.mf_result = result