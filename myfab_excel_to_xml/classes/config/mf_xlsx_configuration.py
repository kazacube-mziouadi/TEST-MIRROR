# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_xlsx_configuration(models.Model):
    _name = 'mf.xlsx.configuration'
    
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(required=True)
    root_beacon = fields.Char(required=True)
    sheet_ids = fields.One2many('mf.xlsx.config.sheet', 'excel_configuration_id', string='Sheets', copy=True)
