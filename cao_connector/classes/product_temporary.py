# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError, ValidationError

class product_product_temporary(models.Model):
    _name = 'product.product.temporary'
    _inherit = 'product.product'
    _description = 'Product temporary'

    mf_is_selected = fields.Boolean(string='Selected', default=True)
    mf_xml_import_processing_id = fields.Many2one('xml.import.processing.history', string='Processing', ondelete='cascade', readonly=True)

    @api.one
    @api.depends('name')
    def get_corresponding_product(self):
        temporary_id = self.id
        product_rc = self.env['product.product'].search([('name', '=', self.name)])
        if product_rc:
            self = product_rc
            self.id = temporary_id