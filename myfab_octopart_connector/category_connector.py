# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from docutils.nodes import field
from openerp.exceptions import ValidationError
import json
import urllib
import urllib2

class connector_category(models.Model):
    _name = 'octopart.category'

    _description = 'Category from Octopart'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(string="Name")
    complete_path = fields.Char(compute='_compute_complete_path', string="Full path")
    uid = fields.Char(string="Octopart id")
    parent_uid = fields.Char(string="Ocotpart Parent id")
    ancestor_uids = fields.Char()
    num_parts = fields.Integer(string='Component number')
    parent_id = fields.Many2one('octopart.category', compute='_compute_parent_id', string="Parent")
    characteristics_type_ids = fields.Many2many('characteristic.type', string='Spec type')
    characteristics_value_ids = fields.Many2many('characteristic.value', string='Spec value')
    apiKey = fields.Char(compute='_compute_apiKey')
    
    @api.one
    def _compute_apiKey(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        if search_api_key:
            self.apiKey = search_api_key[0].octopart_api_key

            
    @api.multi
    def name_get(self):
        result = self.custom_name_get()
        if not result:
            result = []
            for categ_rc in self:
                display_name = categ_rc.name
                if categ_rc.parent_id:
                    id_parent = categ_rc.parent_id
                    while id_parent and id_parent.name:   
                        display_name = id_parent.name + '/' + display_name
                        id_parent = id_parent.parent_id
                result.append((categ_rc.id, display_name))
        
        return result
    
    @api.one
    def _compute_parent_id(self):
        
        search_category = self.env['octopart.category'].search([['uid', '=', self.parent_uid], ])
        if search_category:
            self.parent_id = search_category[0].id
        return True

    @api.one 
    def _compute_complete_path(self):
        
        self.complete_path = self.name
        if self.parent_id:
            id_parent = self.parent_id
            while id_parent and id_parent.name:
                self.complete_path = id_parent.name + '/' + self.complete_path
                id_parent = id_parent.parent_id
        
        return True
    
    
    @api.multi
    def get_characteristics(self):
        if self.apiKey:
            res = self.send_V4()
            search_result = json.loads(res)
        else:
            raise Warning(_("You do not have a key to connect to Octopart."))  
            
        #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
        if 'errors' in search_result.keys():            
            raise ValidationError(search_result['errors'][0]['message'])
            
        attributes = search_result['data']['categories'][0]['relevant_attributes']        
        for attribute in attributes:
            self.characteristics_manager(attribute)

        return True
    

#Méthode pour le création ou la modification des characteristic
    def characteristics_manager(self, current_attributs):
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
            
        if self.id not in active_spec_rc.octopart_category_ids.ids:
            active_spec_rc.write({'octopart_category_ids' : [(4, self.id)],  })
                
        return True


#méthode envoie et récupération de donnée serveur
    def send_V4(self):
        ids = [str(self.uid)]
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
