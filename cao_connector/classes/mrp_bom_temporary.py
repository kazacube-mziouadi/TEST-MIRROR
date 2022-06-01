# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError, ValidationError

class mrp_bom(models.Model):
    _name = 'mrp.bom.temporary'
    _inherit = 'mrp.bom'
    _description = 'Bill of Material temporary'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    #Entête
    product_id = fields.Many2one('product.product.temporary', string='Product', select=True, required=False, ondelete='restrict')
    bom_ids = fields.One2many('mrp.bom.temporary', 'bom_id',  string='Component', copy=True)

    @api.one
    def get_existing_mrp_bom(self):
        mrp_bom_id = self.id
        mrp_bom_rc = self.env['mrp.bom'].search([('product_id', '=', self.product_id)])
        if mrp_bom_rc:
            self = mrp_bom_rc
            self.id = mrp_bom_id