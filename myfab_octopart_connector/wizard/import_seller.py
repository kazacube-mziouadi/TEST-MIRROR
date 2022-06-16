# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
import openerp.addons.decimal_precision as dp
from openerp.addons.base_openprod.common import get_form_view
import json
import urllib
import urllib2
import base64

class import_seller_wizard(models.TransientModel):
    _name = 'import.seller.wizard'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    explaination = fields.Text(default=(_('Select import sellers to import all available sellers from Octopart to Openprod.')))
    apiKey = fields.Char(compute='_compute_apiKey')
    
    @api.one
    def _compute_apiKey(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        if search_api_key:
            self.apiKey = search_api_key[0].octopart_api_key
            
    @api.multi
    def request_seller(self):
        if self.apiKey:
            res = self.send_V4()
            search_result = json.loads(res)
        else:
            raise Warning(_("You do not have a key to connect to Octopart."))  
        
        #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
        if 'errors' in search_result.keys():            
            raise ValidationError(search_result['errors'][0]['message'])
            
        sellers_res = search_result['data']['sellers']
        for seller in sellers_res: 
            self.category_seller(seller)

        return True
    

#Méthode pour le création ou la modification des categorie
    def category_seller(self, current_seller):
        search_seller = self.env['connector.seller'].search([['octopart_uid', '=', current_seller['id']], ])
        if len(search_seller) == 0:
            result_recherche  = self.env['connector.seller'].create({
                'name' : current_seller['name'],
                'octopart_uid' : current_seller['id'],
                'homepage_url' : current_seller['homepage_url'],
                'display_flag' : current_seller['slug'],
                'is_verified' : current_seller['is_verified'],
                'is_distributorapi' : current_seller['is_distributorapi'],
            })
        elif len(search_seller) == 1:
            search_seller.write({
                'name' : current_seller['name'],
                'homepage_url' : current_seller['homepage_url'],
                'display_flag' : current_seller['slug'],
                'is_verified' : current_seller['is_verified'],
                'is_distributorapi' : current_seller['is_distributorapi'],
            })
        else:
            raise
        
        return True


#méthode envoie et récupération de donnée serveur
    def send_V4(self):
        url = 'https://octopart.com/api/v4/endpoint'
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        headers['token'] = '{}'.format(self.apiKey)
        data = {'query': self.query_def()}
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
        query Query_Seller{
            sellers{
                id
                name
                aliases
                homepage_url
                slug
                is_verified
                is_distributorapi
              }
        }
        
        '''
        return query
        