# -*- coding: utf-8 -*-

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class technical_data_config_settings(models.Model):
    _inherit = 'technical.data.config.settings'
    
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char()
    octopart_api_key = fields.Char()
