# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class octopart_seller(models.Model):
    _name = 'octopart.seller'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(required=True)
    octopart_uid = fields.Char(required=True)
    homepage_url = fields.Char()
    octopart_name = fields.Char()
    is_verified = fields.Boolean(string="Is verified", default=False, help="True if a manufacturer participates in Octopart's Verified Manufacturer program.")
    is_distributorapi = fields.Boolean(string="Is distributor", default=False, help="True if a distributor is integrated into the Octopart API feedback to provide the latest price and stock data.")
    has_ecommerce = fields.Boolean()
    