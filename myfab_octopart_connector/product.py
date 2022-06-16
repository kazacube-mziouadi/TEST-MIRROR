# -*- coding: utf-8 -*-
from openerp import models, api, fields
from openerp.exceptions import ValidationError
import json
import urllib
import urllib2


class product(models.Model):
    _inherit = 'product.product'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    octopart_uid_product = fields.Char()
    manufacturer_id = fields.Many2one('octopart.manufacturer', string='Manufacturer')
    manufacturer_code = fields.Char()

    
    @api.multi
    def request_update_price(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        if search_api_key:
            api_Key = search_api_key[0].octopart_api_key
            if api_Key:
                res = self.send_request(api_Key)
                search_result = json.loads(res)
            else:
                raise UserWarning(_("You must have an Octopart key to use this action."))  
               
            #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
            if 'errors' in search_result.keys():            
                raise ValidationError(search_result['errors'][0]['message'])   
               
            sellers_res = search_result['data']['parts'][0]['sellers']
            for seller in sellers_res: 
                self.update_price(seller)
    
            return True
        
        return False
    
    
    #méthode envoie et récupération de donnée serveur
    def send_request(self, api_key):
        ids = [str(self.octopart_uid_product)]
        variables = {'ids': ids}
        url = 'https://octopart.com/api/v4/endpoint'
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        headers['token'] = '{}'.format(api_key)
        data = {'query': self.query_def(),
                'variables': variables}
        req = urllib2.Request(url, json.dumps(data).encode('utf-8'), headers)
        try:
            response = urllib2.urlopen(req)
            return response.read().decode('utf-8')
        except urllib2.HTTPError as e:
            print((e.read()))
            print('')
            raise e
    
    
    #construtction de la requête 
    def query_def(self):
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
    
    
    @api.multi
    def update_price(self, current_seller):        
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