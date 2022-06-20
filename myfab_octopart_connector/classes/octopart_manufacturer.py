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
    is_verified = fields.Boolean(string=" Is verified", default=False, help="True if a manufacturer participates in Octopart's Verified Manufacturer program.")
    is_distributorapi = fields.Boolean(string="Is distributor", default=False, help="True if a distributor has an API integration with Octopart to provide latest pricing and stock data.")
    part_in_openprod = fields.Integer(compute='_compute_in_openprod')
    
    def _compute_in_openprod(self):
        search_product = self.env['product.product'].search_count([['manufacturer_id', '=', self.id], ])
        self.part_in_openprod = search_product
        
        return True