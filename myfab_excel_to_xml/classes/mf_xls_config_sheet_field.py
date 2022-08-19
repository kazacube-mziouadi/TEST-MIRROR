# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_xls_config_sheet_field(models.Model):
    _name = 'mf.xls.config.sheet.field'
    _order = 'sequence'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    sequence = fields.Integer(default=0, required=True)
    excel_sheet_id = fields.Many2one('mf.xls.config.sheet', string='Sheet', required=True, ondelete='cascade')
    writing_mode = fields.Selection('_type_get', string='Writing mode', required=True, default='column_value')
    column = fields.Char(required=True, help='Data column in XLSX file')
    fixed_value = fields.Char(required=True, help='Fixed value')
    beacon = fields.Char(required=True)
    attribute = fields.Char()
    is_merge_attributes = fields.Boolean(string='Merge attributes in beacon', default=True)
    value = fields.Char(compute="_mf_compute_value")

    def _type_get(self):
        return [
            ('column_value', _('Column value')),
            ('constant_value', _('Constant value')),
        ]
        
    def _mf_compute_value(self):
        if self.writing_mode == 'column_value':
            self.value = self.column
        elif self.writing_mode == 'constant_value':
            self.value = self.fixed_value
        else:
            self.value = ""