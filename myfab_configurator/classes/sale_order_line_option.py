# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class sale_order_line_option(models.Model):
    """ 
        Sale order line option
    """
    _inherit = 'sale.order.line.option'

    #===========================================================================
    # SQL
    #===========================================================================
    _order = 'mf_sequence asc'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    mf_sequence = fields.Integer(string=_('Sequence'), related='option_id.mf_sequence', readonly=True, store=True)

