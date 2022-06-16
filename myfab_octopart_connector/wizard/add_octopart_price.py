# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.addons.base_openprod.common import get_form_view
from openerp.exceptions import ValidationError
import json
import urllib
import urllib2

class octopart_price_add(models.TransientModel):
    _name = 'octopart.price.add'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    part_uid_octopart = fields.Char(string="Part Octopart id", required=True)
    list_seller_offers_ids = fields.One2many('octopart.seller.offer', 'add_price_id', string='Offers')
    company_id = fields.Many2one('res.company', string='Company', required=True, ondelete='restrict', default=lambda self: self.env.user.company_id)
    uop_id = fields.Many2one('product.uom', string='UoP',required=True, ondelete='restrict', help='Unit of Purchase')
    uoi_id = fields.Many2one('product.uom', string='UoI',required=True, ondelete='restrict', help='Unit of Invoice')
    product_id = fields.Char(required=True)    
    
    @api.multi
    def show_offer(self):
        self._request_price()
        return {
            'type': 'ir.actions.act_window_no_close'
        }

    def _request_price(self):
        search_result = self.env['octopart.api'].get_api_data(self._set_data())
        if search_result:
            sellers_res = search_result['data']['parts'][0]['sellers']
            for seller in sellers_res: 
                self._offer_management(seller)
            return True
        return False
        
        
    #Méthode pour la création des offre 
    def _offer_management(self, current_seller):
        search_value = self.env['res.partner'].search([['octopart_uid_seller', '=', current_seller['company']['id']], ])
        if len(search_value) > 0:
            company_value = current_seller['company']                 
            for offer in current_seller['offers']:
                add_seller_offer  = self.env['octopart.seller.offer'].create({
                    'name' :company_value['name'], 
                    'seller_identifier' : company_value['id'], 
                    'sku' : offer['sku'],
                    'add_price_id' : self.id
                })
                for price in offer['prices']:
                    # Create price offer in wizard
                    add_price_offer  = self.env['octopart.price.offer'].create({
                        'offer_id' : add_seller_offer.id,
                        'currency' : price['currency'],
                        'price' : price['price'],
                        'number_item' : price['quantity']
                    })
            add_seller_offer.refresh()
        
        return True

    #méthode envoie et récupération de donnée serveur
    def _set_data(self):
        ids = [str(self.part_uid_octopart)]
        variables = {'ids': ids}
        data = {'query': self._query_def(),
                'variables': variables}
        return data

    #construtction de la requête 
    def _query_def(self):
        query ='''
        query Part_Search($ids:[String!]!) {
          parts(ids: $ids, country:"", currency:"", distributorapi_timeout:"3"){
            sellers(authorized_only :true, include_brokers:false, ){
              company{
                id
                name
              }
              offers{
                prices{
                  currency
                  quantity
                  price
                }
                sku
                factory_lead_days
                moq
                inventory_level 
              }
            }
          }
        }
        
        '''
        return query