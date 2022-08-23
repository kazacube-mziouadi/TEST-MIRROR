# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_xlsx_config_sheet(models.Model):
    _name = 'mf.xlsx.config.sheet'
    _order = 'sequence'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    sequence = fields.Integer(default=0, required=True)
    excel_configuration_id = fields.Many2one('mf.xlsx.configuration', string='Excel configuration', required=True, ondelete='cascade')
    sheet_name_or_index = fields.Char(required=True, help='Sheet name or index in XLSX file')
    starting_line = fields.Integer(default=2, help='Row from which data will be read', required=True)
    ending_line = fields.Char(help='Last row from which data will be inserted.', required=False)
    beacon_for_sheet = fields.Char()
    beacon_grouping_fields = fields.Char(required=True)
    level_field_id = fields.Many2one('mf.xlsx.config.sheet.level', string='Level field', ondelete='set null')
    field_ids = fields.One2many('mf.xlsx.config.sheet.field', 'excel_sheet_id', string='Fields', copy=True)