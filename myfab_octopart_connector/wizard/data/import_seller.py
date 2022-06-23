# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class octopart_seller_import_wizard(models.TransientModel):
    _name = 'octopart.seller.import.wizard'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    explaination = fields.Text(default=(_('Select import sellers to import all available sellers from Octopart to Openprod.')))
            
    @api.multi
    def import_sellers(self):
        search_result = self.env['octopart.api.service'].get_api_data(self._get_request_body())
        if search_result:
            sellers_res = search_result['data']['sellers']
            for seller in sellers_res: 
                self._seller_management(seller)
            return True
        return False
    

    #Méthode pour le création ou la modification des vendeurs
    def _seller_management(self, current_seller):
        search_seller = self.env['octopart.seller'].search([['octopart_uid', '=', current_seller['id']], ])
        if len(search_seller) == 0:
            search_seller = self.env['octopart.seller'].create({
                'name' : current_seller['name'],
                'octopart_uid' : current_seller['id'],
                'homepage_url' : current_seller['homepage_url'],
                'octopart_name' : current_seller['slug'],
                'is_verified' : current_seller['is_verified'],
                'is_distributorapi' : current_seller['is_distributorapi'],
            })
        elif len(search_seller) == 1:
            search_seller.write({
                'name' : current_seller['name'],
                'homepage_url' : current_seller['homepage_url'],
                'octopart_name' : current_seller['slug'],
                'is_verified' : current_seller['is_verified'],
                'is_distributorapi' : current_seller['is_distributorapi'],
            })
        else:
            raise
        
        return True


    #méthode envoie et récupération de donnée serveur
    def _get_request_body(self):
        data = {'query': self._query_def()}
        return data

    #construtction de la requête 
    def _query_def(self):
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
        