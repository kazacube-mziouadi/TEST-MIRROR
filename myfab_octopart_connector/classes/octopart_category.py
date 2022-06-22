# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import json

class octopart_category(models.Model):
    _name = 'octopart.category'

    _description = 'Category Octopart'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char()
    octopart_uid = fields.Char()
    complete_path = fields.Char(compute='_compute_complete_path', string="Full path")
    octopart_parent_uid = fields.Char()
    number_of_products = fields.Integer(string='Number of products')
    parent_id = fields.Many2one('octopart.category', compute='_compute_parent_id', string="Parent")
    characteristics_type_ids = fields.Many2many('characteristic.type', string='Characteristic type')
    characteristics_value_ids = fields.Many2many('characteristic.value', string='Characteristic value')
               
    @api.one 
    def _compute_complete_path(self):
        self.complete_path = self.name
        if self.parent_id:
            id_parent = self.parent_id
            while id_parent and id_parent.name:
                self.complete_path = id_parent.name + '/' + self.complete_path
                id_parent = id_parent.parent_id
        
        return True
    
    @api.one
    def _compute_parent_id(self):
        search_category = self.env['octopart.category'].search([['octopart_uid', '=', self.octopart_parent_uid], ])
        if search_category and self.id != search_category[0].id:
            self.parent_id = search_category[0].id
        return True

    @api.one
    def get_characteristics(self):
        search_result = self.env['octopart.api'].get_api_data(self._set_data())
        if search_result and len(search_result['data']['categories']) > 0:
            attributes = search_result['data']['categories'][0]['relevant_attributes']        
            for attribute in attributes:
                self.characteristics_management(self.id, attribute)
            return True
        return False
    

#Méthode pour le création ou la modification des characteristic
    def characteristics_management(self, current_id, current_attributs):
        active_spec_rc = False
        spec_octopart = self.env['characteristic.type'].search([('name', '=', current_attributs['name'])])
        if spec_octopart:
            active_spec_rc = spec_octopart[0]
            
        format_characteristic = 'string'
        
        if active_spec_rc:
            active_spec_rc.write({
                'format' : format_characteristic,
                'octopart_key' : current_attributs['shortname'],
            })
        else:    
            active_spec_rc  = self.env['characteristic.type'].create({
                'name' : current_attributs['name'],
                'format' : format_characteristic,
                'octopart_key' : current_attributs['shortname'],
            })
            
        if current_id not in active_spec_rc.octopart_category_ids.ids:
            active_spec_rc.write({'octopart_category_ids' : [(4, current_id)],  })
                
        return active_spec_rc


#méthode envoie et récupération de donnée serveur
    def _set_data(self):
        ids = [str(self.octopart_uid)]
        variables = {'ids': ids}
        data = {'query': self._query_def(),
                'variables': variables}
        return data


#construtction de la requête 
    def _query_def(self):
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
