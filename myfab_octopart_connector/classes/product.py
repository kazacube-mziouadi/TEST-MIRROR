# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import json


class product(models.Model):
    _inherit = 'product.product'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    # Stored in a char field because the octopart product ID is stored in the research result, if it is reset we lose the link
    # in this situation it is better to store it in a char to keep it active
    octopart_uid_product = fields.Char()
    octopart_uid_manufacturer = fields.Many2one('octopart.manufacturer', string='Manufacturer')
    manufacturer_code = fields.Char()

    @api.multi
    def octopart_price_update(self):
        search_result = self.env['octopart.api'].get_api_data(self._set_data())
        if search_result and len(search_result['data']['parts']) > 0:    
            sellers_res = search_result['data']['parts'][0]['sellers']
            for seller in sellers_res: 
                self._update_price(seller)
            return True
        return False
    
    def _update_price(self, current_seller):        
        offers = current_seller['offers']
        for offer in offers:
            for supplyer in self.sinfo_ids:
                if supplyer.partner_id.octopart_uid_seller == current_seller['company']['id']:
                    supplyer.pricelist_ids.unlink()
                    for price in offer['prices']: 
                        if price['currency'] == supplyer.currency_id.name: 
                            item_number = price['quantity']
                            price_octopart = price['price']
                            add_price_offer  = self.env['pricelist.supplierinfo'].create({ 
                                'sinfo_id' : supplyer.id,
                                'price' : price_octopart,
                                'min_qty' : item_number,
                            })
        
        return True
    
    #méthode envoie et récupération de donnée serveur
    def _set_data(self):
        ids = [str(self.octopart_uid_product)]
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
              }
            }
          }
        }
        
        '''
        return query