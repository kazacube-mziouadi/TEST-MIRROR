# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    octopart_uid_seller_id = fields.Many2one('octopart.seller', string='Octopart seller')
    octopart_uid_manufacturer_id = fields.Many2one('octopart.manufacturer', string='Octopart manufacturer')
    
    @api.one
    def reset_octopart_manufacturer_uid(self):
        # Writing False in the octopart_uid_manufacturer_id is like doing "unlink" but it doesn't delete the record
        self.octopart_uid_manufacturer_id = False

    @api.one
    def reset_octopart_seller_uid(self):
        # Writing False in the octopart_uid_seller_id is like doing "unlink" but it doesn't delete the record
        self.octopart_uid_seller_id = False