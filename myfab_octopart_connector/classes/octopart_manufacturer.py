# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class octopart_manufacturer(models.Model):
    _name = 'octopart.manufacturer'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char()
    octopart_uid = fields.Char()
    homepage_url = fields.Char()
    is_verified = fields.Boolean(string="Is verified", default=False, help="True if a manufacturer participates in Octopart's Verified Manufacturer program.")
    is_distributorapi = fields.Boolean(string="Is distributor", default=False, help="True if a distributor is integrated into the Octopart API feedback to provide the latest price and stock data.")
    products_in_openprod = fields.Integer(compute='_compute_is_in_openprod')
    products_ids = result_ids = fields.One2many('product.product', 'octopart_uid_manufacturer', string='Products', readonly=True)
    
    def _compute_is_in_openprod(self):
        self.products_in_openprod = self.env['product.product'].search_count([['octopart_uid_manufacturer', '=', self.id], ])
        return True