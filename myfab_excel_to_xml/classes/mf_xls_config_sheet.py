# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_xls_config_sheet(models.Model):
    _name = 'mf.xls.config.sheet'
    _order = 'sequence'
    _sql_constraints = [
        ('sheet_unique', 'unique(sheet_name, excel_configuration_id)', 'Error : sheet must be unique.'),
    ]

    #===========================================================================
    # COLUMNS
    #===========================================================================
    sequence = fields.Integer(default=0, required=False)
    excel_configuration_id = fields.Many2one('mf.xls.configuration', string='Excel configuration', required=True, ondelete='cascade')
    sheet_name = fields.Char(required=True, help='Name of the sheet in XLSX file')
    starting_line = fields.Integer(default=2, help='Row from which data will be read', required=True)
    ending_line = fields.Char(help='Last row from which data will be inserted.\nYou can use a cell value if you write \'$\' \nExample : $A1', required=False)
    beacon_for_sheet = fields.Char()
    beacon_per_row = fields.Char(required=True)
    level_field_id = fields.Many2one('mf.xls.config.sheet.level', string='Level field', ondelete='set null')
    field_ids = fields.One2many('mf.xls.config.sheet.field', 'excel_sheet_id', string='Fields', copy=True)