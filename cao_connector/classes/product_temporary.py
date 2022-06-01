# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError, ValidationError

class product_temporary(models.TransientModel):
    _name = 'product.product.temporary'
    _inherit = 'product.product'
    _description = 'Product temporary'

    @api.one
    @api.depends('name')
    def get_corresponding_product(self):
        temporary_id = self.id
        product_rc = self.env['product.product'].search([('name', '=', self.name)])
        if product_rc:
            self = product_rc
            self.id = temporary_id