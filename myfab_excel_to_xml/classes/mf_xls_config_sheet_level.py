# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_xls_config_sheet_level(models.Model):
    _name = 'mf.xls.config.sheet.level'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(compute="_mf_compute_name")
    column = fields.Char(required=True, help='Data column in XLSX file')
    is_numerical_level = fields.Boolean(default=True)
    level_separator = fields.Char()
    parent_column = fields.Char(help='Data column where to search current value in XLSX file')
    beacon_per_level_in_parent = fields.Char(required=True)

    @api.one
    def _mf_compute_name(self):
        temp_name = self.beacon_per_level_in_parent + " = " + self.column
        if self.is_numerical_level:
            temp_name += " (Num)"
        else:
            temp_name += " -> " + self.parent_column

        self.name = temp_name