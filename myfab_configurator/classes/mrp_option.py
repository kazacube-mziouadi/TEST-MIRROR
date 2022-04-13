# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class mrp_option(models.Model):
    """ 
        Option
    """
    _inherit = 'mrp.option'

    #===========================================================================
    # SQL
    #===========================================================================
    _order = 'sequence asc'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    sequence = fields.Integer(string='Sequence',required=True, default=10)

