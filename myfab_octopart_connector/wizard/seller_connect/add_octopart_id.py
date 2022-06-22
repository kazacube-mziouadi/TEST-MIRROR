# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class octopart_seller_partner_connect(models.TransientModel):
    _name = 'octopart.seller.partner.connect'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    seller_id = fields.Many2one('octopart.seller', string="Seller", required=True)    
    partner_id = fields.Many2one('res.partner', 'Partner', ondelete='cascade', required=True, domain = "[('is_supplier','=',True), ('octopart_uid_seller','=','0')]")
    list_sellers_ids = fields.One2many('octopart.seller.partner.connect.ids', 'add_octopart_id', string='Octopart sellers list')
    
    @api.multi
    def add_seller_id(self):
        self.partner_id.write({'octopart_uid_seller' : self.seller_id.octopart_uid })

    @api.multi
    def search_seller(self):
        self.list_sellers_ids.unlink() 
        
        result_recherche  = self.env['octopart.seller.partner.connect.ids'].create({
            'name' : self.seller_id.name,
            'uid_octopart' : self.seller_id.octopart_uid,
            'add_octopart_id' : self.id
        })       
        
        return {
            'type': 'ir.actions.act_window_no_close'
        }
          
class octopart_seller_partner_connect_ids(models.TransientModel):
    _name = 'octopart.seller.partner.connect.ids'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(strin="name")  
    uid_octopart = fields.Char(string="Octopart id")
    add_octopart_id = fields.Many2one('octopart.seller.partner.connect', required=True, ondelete='cascade')
    
    @api.multi
    def add_seller_id(self):
        self.add_octopart_id.partner_id.write({'octopart_uid_seller' : self.uid_octopart })
        return {
            'type': 'ir.actions.act_window_no_close'
        }
