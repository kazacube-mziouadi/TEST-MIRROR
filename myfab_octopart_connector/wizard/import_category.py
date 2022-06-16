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
import os

class import_category_wizard(models.TransientModel):
    _name = 'import.category.wizard'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    explaination = fields.Text(default=(_('Select import categories to import all available categories from Octopart to Openprod.')))
    apiKey = fields.Char(compute='_compute_apiKey')
    
    @api.one
    def _compute_apiKey(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        if search_api_key:
            self.apiKey = search_api_key[0].octopart_api_key
        return True
            
    @api.multi
    def request_category(self):
        if self.apiKey:
            res = self.send_V4()
            search_result = json.loads(res)
        else:
            raise UserWarning(_("You do not have a key to connect to Octopart."))  
            
        #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
        if 'errors' in search_result.keys():            
            raise ValidationError(search_result['errors'][0]['message'])
        
        root = search_result['data']['categories'][0]
        self.category_manager(root)

        return True
    

#Méthode pour le création ou la modification des categorie
    def category_manager(self, current_category):
        test_category = self.env['octopart.category'].search([('uid', '=', current_category['id'])])
        if len(test_category) == 0:
            result_recherche  = self.env['octopart.category'].create({
                'name' : current_category['name'],
                'uid' : current_category['id'],
                'parent_uid' : current_category['parent_id'],
                'num_parts' : current_category['num_parts']
            })
        elif len(test_category) == 1:
            test_category.write({
                'name' : current_category['name'],
                'parent_uid' : current_category['parent_id'],
                'num_parts' : current_category['num_parts']
            })
        else:
            raise
        for child in current_category['children']:
            self.category_manager(child)
        
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
        query Query_Category{
            categories{
            id
            name
            path
            num_parts
            parent_id
            children{
              id
              name
              path
              parent_id
              num_parts
              children{
                id
                name
                path
                parent_id
                num_parts
                children{
                  id
                  name
                  path
                  parent_id
                  num_parts
                  children{
                    id
                    name
                    path
                    parent_id
                    num_parts
                    children{
                      id
                      name
                      path
                      parent_id
                      num_parts
                    }
                  }
                }
              }
            }
          }
        }
        
        '''
        return query
    
            