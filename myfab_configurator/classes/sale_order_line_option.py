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
    _order = 'sequence asc'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    sequence = fields.Integer(string='Sequence', readonly=True, store=True)

