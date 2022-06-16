# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from docutils.nodes import field
from openerp.exceptions import ValidationError
import json
import urllib
import urllib2

class octopart_category(models.Model):
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
            
#    @api.multi
#    def name_get(self):
#        result = self.custom_name_get()
#        if not result:
#            result = []
#            for categ_rc in self:
#                display_name = categ_rc.name
#                if categ_rc.parent_id:
#                    id_parent = categ_rc.parent_id
#                    while id_parent and id_parent.name:   
#                        display_name = id_parent.name + '/' + display_name
#                        id_parent = id_parent.parent_id
#                result.append((categ_rc.id, display_name))        
#        return result
    
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
        search_category = self.env['octopart.category'].search([['uid', '=', self.parent_uid], ])
        if search_category and self.id != search_category[0].id:
            self.parent_id = search_category[0].id
        return True

    @api.multi
    def get_characteristics(self):
        search_result = self.env['octopart.api'].get_api_data(self._set_data())
        if search_result:
            attributes = search_result['data']['categories'][0]['relevant_attributes']        
            for attribute in attributes:
                self._characteristics_manager(attribute)
            return True
        return False
    

#Méthode pour le création ou la modification des characteristic
    def _characteristics_manager(self, current_attributs):
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
                
        return active_spec_rc


#méthode envoie et récupération de donnée serveur
    def _set_data(self):
        ids = [str(self.uid)]
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
