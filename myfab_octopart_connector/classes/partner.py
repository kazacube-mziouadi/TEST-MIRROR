# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    octopart_uid_seller = fields.Char(default="0", string="Octopart seller id")
    octopart_uid_manufacturer = fields.Char(default="0", string="Octopart manufacturer id")
    
    @api.multi
    def reset_octopart_seller_uid(self):
        self.write({'octopart_uid_seller' : '0' })
        return True

    @api.multi
    def reset_octopart_manufacturer_uid(self):
        self.write({'octopart_uid_manufacturer' : '0' })
        return True