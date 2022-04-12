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
    _order = 'mf_sequence asc'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    mf_sequence = fields.Integer(string=_('Sequence'), required=True, default=10)

