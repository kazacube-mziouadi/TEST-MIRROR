# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_modules_config(models.Model):
    _inherit ='mf.modules.config'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    default_processing_wizard = fields.Many2one('xml.import.processing', string="Default processing")
    default_stop_at_simulation = fields.Boolean(string='Default stop at simulation')
