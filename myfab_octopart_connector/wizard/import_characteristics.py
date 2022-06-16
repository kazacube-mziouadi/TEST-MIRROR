# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.addons.base_openprod.common import get_form_view
from openerp.exceptions import ValidationError
import json
import urllib
import urllib2
import base64
import os

class import_characteristics_wizard(models.TransientModel):
    _name = 'import.characteristics.wizard'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    explaination = fields.Text(default=(_('Import characteristics of all select octopart category')))
    apiKey = fields.Char(compute='_compute_apiKey')
    
    @api.one
    def _compute_apiKey(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        if search_api_key:
            self.apiKey = search_api_key[0].octopart_api_key
        return True
    
    
    @api.multi
    def resquest_characteristics(self):
        ids = self.env.context.get('active_ids')
        if self.apiKey:
            for id in ids:
                category_rc = self.env['octopart.category'].search([('id', '=', id)])
                res = self.send_V4(category_rc.uid)
                search_result = json.loads(res)
                
                #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
                if 'errors' in search_result.keys():            
                    raise ValidationError(search_result['errors'][0]['message'])
                
                if len(search_result['data']['categories']) > 0:
                    attributes = search_result['data']['categories'][0]['relevant_attributes']        
                    for attribute in attributes:
                        self.characteristics_manager(attribute, id)
        else:
            raise Warning(_("You do not have a key to connect to Octopart."))  
            
        return True
    

    #Méthode pour le création ou la modification des characteristic
    def characteristics_manager(self, current_attributs, current_id):
        updating = False 
        spec_octopart = self.env['characteristic.type'].search([('name', '=', current_attributs['name'])])
        if spec_octopart:
            active_spec_rc = spec_octopart[0]
            updating = True
            
        format_characteristic = 'string'
        
        if updating:
            active_spec_rc.write({
                'format' : format_characteristic,
                'octopart_key' : current_attributs['shortname'],
            })
        else:    
            add_characteristic_type  = self.env['characteristic.type'].create({
                'name' : current_attributs['name'],
                'format' : format_characteristic,
                'octopart_key' : current_attributs['shortname'],
            })
            active_spec_rc = add_characteristic_type
            
        if current_id not in active_spec_rc.octopart_category_ids.ids:
            active_spec_rc.write({'octopart_category_ids' : [(4, current_id)],  })
                
        return True


    #méthode envoie et récupération de donnée serveur
    def send_V4(self, current_id):
        ids = [str(current_id)]
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
        query Query_Characteristics($ids: [String!]!) {
            categories(ids:$ids){
                relevant_attributes{
                  id
                  name
                  shortname
                  group
                }
            }
        }
        
        '''
        return query