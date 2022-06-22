# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import json

class octopart_category_import_wizard(models.TransientModel):
    _name = 'octopart.category.import.wizard'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    explaination = fields.Text(default=(_('Select import categories to import all available categories from Octopart to Openprod.')))
            
    @api.multi
    def import_categories(self):
        search_result = self.env['octopart.api'].get_api_data(self._set_data())
        if search_result:
            root = search_result['data']['categories'][0]
            self._category_management(root)
            return True
        return False
    

    #Méthode pour le création ou la modification des categorie
    def _category_management(self, current_category):
        test_category = self.env['octopart.category'].search([('octopart_uid', '=', current_category['id'])])
        if len(test_category) == 0:
            result_recherche  = self.env['octopart.category'].create({
                'name' : current_category['name'],
                'octopart_uid' : current_category['id'],
                'octopart_parent_uid' : current_category['parent_id'],
                'number_of_products' : current_category['number_of_products']
            })
        elif len(test_category) == 1:
            test_category.write({
                'name' : current_category['name'],
                'octopart_parent_uid' : current_category['parent_id'],
                'number_of_products' : current_category['number_of_products']
            })
        else:
            raise

        for child in current_category['children']:
            self._category_management(child)
        
        return True


    #méthode envoie et récupération de donnée serveur
    def _set_data(self):
        data = {'query': self._query_def()}
        return data

    #construtction de la requête 
    def _query_def(self):
        query ='''
        query Query_Category{
            categories{
            id
            name
            path
            number_of_products
            parent_id
            children{
              id
              name
              path
              parent_id
              number_of_products
              children{
                id
                name
                path
                parent_id
                number_of_products
                children{
                  id
                  name
                  path
                  parent_id
                  number_of_products
                  children{
                    id
                    name
                    path
                    parent_id
                    number_of_products
                    children{
                      id
                      name
                      path
                      parent_id
                      number_of_products
                    }
                  }
                }
              }
            }
          }
        }
        
        '''
        return query
    
            