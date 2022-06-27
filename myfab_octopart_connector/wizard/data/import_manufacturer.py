# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class octopart_manufacturer_import_wizard(models.TransientModel):
    _name = 'octopart.manufacturer.import.wizard'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    explaination = fields.Text(default=(_('Select import manufacturer to import all available manufacturer from Octopart to Openprod.')))       
        
    @api.multi
    def import_manufacturers(self):
        search_result = self.env['octopart.api.service'].get_api_data(self._get_request_body())
        if search_result:
            manufacturers_res = search_result['data']['manufacturers']
            for manufacturer in manufacturers_res: 
                self._manufacturer_management(manufacturer)
            return True
        return False
            
        
    #Méthode pour le création ou la modification des fabricans
    def _manufacturer_management(self, current_manufacturer):
        search_manufacturer = self.env['octopart.manufacturer'].search([['octopart_uid', '=', current_manufacturer['id']], ])
        if len(search_manufacturer) == 0:
            search_manufacturer = self.env['octopart.manufacturer'].create({
                'name' : current_manufacturer['name'],
                'octopart_uid' : current_manufacturer['id'],
                'homepage_url' : current_manufacturer['homepage_url'],
                'is_verified' : current_manufacturer['is_verified'],
                'is_distributorapi' : current_manufacturer['is_distributorapi'],
            })
        elif len(search_manufacturer) == 1:
            search_manufacturer.write({
                'name' : current_manufacturer['name'],
                'homepage_url' : current_manufacturer['homepage_url'],
                'is_verified' : current_manufacturer['is_verified'],
                'is_distributorapi' : current_manufacturer['is_distributorapi'],
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
        query Query_Manufacturer{
            manufacturers{
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