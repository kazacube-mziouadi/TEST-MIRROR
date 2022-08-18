# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_xls_configuration(models.Model):
    _name = 'mf.xls.configuration'
    
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(required=True)
    root_beacon = fields.Char(required=True)
    sheet_ids = fields.One2many('mf.xls.config.sheet', 'excel_configuration_id', string='Sheets', copy=True)
