# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.addons.base_openprod.common import get_form_view
import json
import urllib
import urllib2
import base64

class import_manufacturer_wizard(models.TransientModel):
    _name = 'import.manufacturer.wizard'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    explaination = fields.Text(default=(_('Select import manufacturer to import all available manufacturer from Octopart to Openprod.')))
    apiKey = fields.Char(compute='_compute_apiKey')
    
    @api.one
    def _compute_apiKey(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        if search_api_key:
            self.apiKey = search_api_key[0].octopart_api_key
        
        
    @api.multi
    def request_manufacturer(self):
        if self.apiKey:
            res = self.send_request()
            search_result = json.loads(res)
        else:
            raise Warning(_("You do not have a key to connect to Octopart."))  
        
        #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
        if 'errors' in search_result.keys():            
            raise ValidationError(search_result['errors'][0]['message'])
            
        manufacturers_res = search_result['data']['manufacturers']
        for manufacturer in manufacturers_res: 
            self.manufacturer_management(manufacturer)

        return True
            
        
    #Méthode pour le création ou la modification des fabricans
    def manufacturer_management(self, current_manufacturer):
        search_manufacturer = self.env['octopart.manufacturer'].search([['octopart_uid', '=', current_manufacturer['id']], ])
        if len(search_manufacturer) == 0:
            result_recherche  = self.env['octopart.manufacturer'].create({
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
    def send_request(self):
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