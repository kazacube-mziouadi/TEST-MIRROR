# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class product(models.Model):
    _inherit = 'product.product'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    # Stored in a char field because the octopart product ID is stored in the research result, if it is reset we lose the link
    # in this situation it is better to store it in a char to keep it active
    octopart_uid_product = fields.Char()
    octopart_uid_manufacturer_id = fields.Many2one('octopart.manufacturer', string='Octopart manufacturer')
    manufacturer_code = fields.Char()

    @api.multi
    def octopart_price_update(self):
        search_result = self.env['octopart.api.service'].get_api_data(self._get_request_body())
        if search_result and len(search_result['data']['parts']) > 0:    
            sellers_res = search_result['data']['parts'][0]['sellers']
            for seller in sellers_res: 
                self._update_price(seller)
            return True
        return False
    
    def _update_price(self, current_seller):  
        for offer in current_seller['offers']:
            for supplier in self.sinfo_ids:
                if supplier.partner_id.octopart_uid_seller_id.octopart_uid == current_seller['company']['id']:
                    # TODO : vérifier le fonctionnement et adapter pour ne pas effacer tous les tarifs
                    supplier.pricelist_ids.unlink()
                    for price in offer['prices']: 
                        if price['currency'] == supplier.currency_id.name:
                            self.env['pricelist.supplierinfo'].create({
                              'sinfo_id' : supplier.id,
                              'price' : price['price'],
                              'min_qty' : price['quantity']
                            })

        return True
    
    #méthode envoie et récupération de donnée serveur
    def _get_request_body(self):
        variables = {'ids': [str(self.octopart_uid_product)]}
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