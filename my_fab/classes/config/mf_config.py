# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class mf_modules_config(models.Model):
    _name ='mf.modules.config'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(required=True, default="myfab configuration")
