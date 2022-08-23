# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_xlsx_config_sheet_field(models.Model):
    _name = 'mf.xlsx.config.sheet.field'
    _order = 'sequence'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    sequence = fields.Integer(default=0, required=True)
    excel_sheet_id = fields.Many2one('mf.xlsx.config.sheet', string='Sheet', required=True, ondelete='cascade')
    writing_mode = fields.Selection('_mf_type_get', string='Writing mode', required=True, default='column_value')
    column = fields.Char(help='Data column in XLSX file')
    fixed_value = fields.Char(help='Fixed value')
    beacon = fields.Char(required=True)
    attribute = fields.Char()
    is_merge = fields.Boolean(string='Merge values in same attributes/beacon', default=True)
    value = fields.Char(compute='_mf_compute_value', readonly=True)

    def _mf_type_get(self):
        return [
            ('column_value', _('Column value')),
            ('constant_value', _('Constant value')),
        ]

    @api.one
    @api.onchange('writing_mode', 'column', 'fixed_value')
    def _mf_compute_value(self):
        temp_value = ''
        if self.writing_mode == 'column_value':
            temp_value = self.column
        elif self.writing_mode == 'constant_value':
            temp_value = self.fixed_value
        self.update({
            "value": temp_value,
        })