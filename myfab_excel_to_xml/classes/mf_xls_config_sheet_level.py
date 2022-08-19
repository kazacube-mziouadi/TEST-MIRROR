# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_xls_config_sheet_level(models.Model):
    _name = 'mf.xls.config.sheet.level'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    sheet_ids = fields.One2many('mf.xls.config.sheet', 'level_field_id', string='Sheets')
    name = fields.Char(compute="_mf_compute_name")
    column = fields.Char(required=True, help='Data column in XLSX file')
    is_numerical_level = fields.Boolean(default=True)
    level_separator = fields.Char()
    parent_reference_column = fields.Char(help='Data column where to search current value in XLSX file')
    beacon_per_level = fields.Char(required=True)

    @api.one
    def _mf_compute_name(self):
        temp_name = self.beacon_per_level + " = " + self.column
        if self.is_numerical_level:
            temp_name += " (Num)"
        else:
            temp_name += " -> " + self.parent_reference_column

        self.name = temp_name