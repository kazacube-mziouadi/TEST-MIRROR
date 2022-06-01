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
    product_id = fields.Many2one('product.product.temporary', string='Product', select=True, required=False, ondelete='restrict')
    bom_ids = fields.One2many('mrp.bom.temporary', 'bom_id',  string='Component', copy=True)

    @api.one
    @api.depends('product_id')
    def get_corresponding_mrp_bom(self):
        temporary_id = self.id
        mrp_bom_rc = self.env['mrp.bom'].search([('product_id', '=', self.product_id.id)])
        if mrp_bom_rc:
            self = mrp_bom_rc
            self.id = temporary_id