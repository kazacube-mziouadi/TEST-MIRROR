# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class octopart_price_add(models.TransientModel):
    _name = 'octopart.price.add'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    product_octopart_uid = fields.Char(string="Product Octopart id", required=True)
    sellers_offers_ids = fields.One2many('octopart.seller.offer', 'add_price_id', string='Offers')
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
        search_result = self.env['octopart.api.service'].get_api_data(self._get_request_body())
        if search_result and len(search_result['data']['parts']) > 0:
            sellers_res = search_result['data']['parts'][0]['sellers']
            for seller in sellers_res: 
                self._offer_management(seller)
            return True
        return False
        
        
    #Méthode pour la création des offre 
    def _offer_management(self, current_seller):
        search_value = self.env['res.partner'].search([['octopart_uid_seller_id', '=', current_seller['company']['id']], ])
        if len(search_value) > 0:
            company_value = current_seller['company']   
            for offer in current_seller['offers']:
                add_price_offers = []
                for price in offer['prices']:
                    # Create price offer in wizard
                    add_price_offers.append((0,0,{
                        'currency' : price['currency'],
                        'price' : price['price'],
                        'minimum_order_quantity' : price['quantity']
                    }))

                self.sellers_offers_ids = [(0,0,{
                    'name' :company_value['name'], 
                    'seller_octopart_uid' : company_value['id'], 
                    'sku' : offer['sku'],
                    'price_ids' : add_price_offers,
                })]
        
        return True

    #méthode envoie et récupération de donnée serveur
    def _get_request_body(self):
        variables = {'ids': [str(self.product_octopart_uid)]}
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