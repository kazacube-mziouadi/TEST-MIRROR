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
    display_flag = fields.Char()
    is_verified = fields.Boolean(string=" Is verified", default=False, help="True if a manufacturer participates in Octopart's Verified Manufacturer program.")
    is_distributorapi = fields.Boolean(string="Is distributor", default=False, help="True if a distributor has an API integration with Octopart to provide latest pricing and stock data.")
    has_ecommerce = fields.Boolean()