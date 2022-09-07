# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_xlsx_configuration(models.Model):
    _name = 'mf.xlsx.configuration'
    
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(required=True)
    main_xml_beacon = fields.Char(required=True)
    csv_file_separator = fields.Char(default=';')
    csv_file_quoting = fields.Char()
    csv_file_encoding = fields.Char(default="utf-8")
    sheet_ids = fields.One2many('mf.xlsx.config.sheet', 'excel_configuration_id', string='Sheets', copy=True)
