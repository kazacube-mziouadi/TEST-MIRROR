# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import except_orm, ValidationError

class stock_quality_control(models.Model):
    """ 
    Stock quality control
    """
    _inherit = 'stock.quality.control'
    
    @api.model
    def _type_get(self):
        res = super(stock_quality_control, self)._type_get()
        res.extend([
                    ('mf_pdf_call_tender_mail', _('Call tender (PDF)')),
                    ])
        return res