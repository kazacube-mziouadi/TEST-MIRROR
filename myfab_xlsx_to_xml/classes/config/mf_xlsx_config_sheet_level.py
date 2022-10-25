# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_xlsx_config_sheet_level(models.Model):
    _name = 'mf.xlsx.config.sheet.level'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    sheet_ids = fields.One2many('mf.xlsx.config.sheet', 'level_field_id', string='Sheets')
    name = fields.Char(compute="_mf_compute_name", readonly=True)
    column = fields.Char(required=True, help='Data column in XLSX file')
    is_level_mono_column = fields.Boolean(default=True)
    level_separator = fields.Char()
    parent_reference_column = fields.Char(help='Data column where to search current value in XLSX file')
    xml_beacon_grouping_children_level = fields.Char()
    parent_xml_beacon_new_name = fields.Char()

    @api.one
    def _mf_compute_name(self):
        temp_name = self.column
        if self.is_level_mono_column:
            if self.level_separator: temp_name += " (" + "sep" + " '" + self.level_separator + "')"
        else:
            if self.parent_reference_column: temp_name += " " + "ref" + " " + self.parent_reference_column
        if self.xml_beacon_grouping_children_level:
            temp_name += " \ " + _("add") + " : " + self.xml_beacon_grouping_children_level
        if self.parent_xml_beacon_new_name:
            temp_name += " \ " + "parent" + " = " + self.parent_xml_beacon_new_name
        self.name = temp_name