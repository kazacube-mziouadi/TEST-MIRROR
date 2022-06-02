# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError, ValidationError

class product_product_temporary(models.Model):
    _name = 'product.product.temporary'
    _inherit = 'product.product'
    _description = 'Product temporary'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    mf_is_selected = fields.Boolean(string='Selected', default=True)
    mf_xml_import_processing_id = fields.Many2one('xml.import.processing.history', string='Processing', ondelete='cascade', readonly=True)