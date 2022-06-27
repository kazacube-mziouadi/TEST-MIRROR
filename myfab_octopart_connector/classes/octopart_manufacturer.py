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
    number_of_products = fields.Integer(compute='_compute_number_of_products_in_openprod',string="Number of products in Openprod")
    products_ids = fields.One2many('product.product', 'octopart_uid_manufacturer_id', string='Products', readonly=True)
    
    @api.one
    def _compute_number_of_products_in_openprod(self):
        self.number_of_products = len(self.products_ids)