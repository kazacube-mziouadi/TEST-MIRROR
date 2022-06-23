# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    octopart_uid_seller = fields.Many2one('octopart.seller', string='Octopart seller')
    octopart_uid_manufacturer = fields.Many2one('octopart.manufacturer', string='Octopart manufacturer')
    
    @api.multi
    def reset_octopart_seller_uid(self):
        self.octopart_uid_seller.unlink()
        return True

    @api.multi
    def reset_octopart_manufacturer_uid(self):
        self.octopart_uid_manufacturer.unlink()
        return True