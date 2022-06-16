# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.addons.base_openprod.common import get_form_view
from openerp.exceptions import ValidationError
import json
import urllib
import urllib2

class add_octopart_price(models.TransientModel):
    _name = 'add.octopart.price'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    part_uid_octopart = fields.Char(string="Part Octopart id", required=True)
    list_seller_offers_ids = fields.One2many('sellers.offers', 'add_price_id', string='Offers')
    company_id = fields.Many2one('res.company', string='Company', required=True, ondelete='restrict', default=lambda self: self.env.user.company_id)
    uop_id = fields.Many2one('product.uom', string='UoP',required=True, ondelete='restrict', help='Unit of Purchase')
    uoi_id = fields.Many2one('product.uom', string='UoI',required=True, ondelete='restrict', help='Unit of Invoice')
    product_id = fields.Char(required=True)
    apiKey = fields.Char(compute='_compute_apiKey')
    
    @api.one
    def _compute_apiKey(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        if search_api_key:
            self.apiKey = search_api_key[0].octopart_api_key
    
    
    api.multi
    def request_price(self):
        if self.apiKey:
            res = self.send_request()
            search_result = json.loads(res)
        else:
            raise UserWarning(_("You must have an Octopart key to use this action."))  
            
        #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
        if 'errors' in search_result.keys():            
            raise ValidationError(search_result['errors'][0]['message'])
            
        sellers_res = search_result['data']['parts'][0]['sellers']
        for seller in sellers_res: 
            self.offer_managere(seller)

        return True
        
        
    #Méthode pour la création des offre 
    def offer_managere(self, current_seller):
        search_value = self.env['res.partner'].search([['octopart_uid_seller', '=', current_seller['company']['id']], ])
        if len(search_value) > 0:
            company_value = current_seller['company']                 
            for offer in current_seller['offers']:
                add_seller_offer  = self.env['sellers.offers'].create({
                    'name' :company_value['name'], 
                    'seller_identifier' : company_value['id'], 
                    'sku' : offer['sku'],
                    'add_price_id' : self.id
                })
                for price in offer['prices']:
                    # Create price offer in wizard
                    add_price_offer  = self.env['price.offer'].create({
                        'offer_id' : add_seller_offer.id,
                        'currency' : price['currency'],
                        'price' : price['price'],
                        'number_item' : price['quantity']
                    })
            add_seller_offer.refresh()
        
        return True


    #méthode envoie et récupération de donnée serveur
    def send_request(self):
        ids = [str(self.part_uid_octopart)]
        variables = {'ids': ids}
        url = 'https://octopart.com/api/v4/endpoint'
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        headers['token'] = '{}'.format(self.apiKey)
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
        
    
    @api.multi
    def show_offer(self):
        self.request_price()
        return {
            'type': 'ir.actions.act_window_no_close'
        }
        
        
    @api.multi
    def add_price_all(self):
        
        return True
