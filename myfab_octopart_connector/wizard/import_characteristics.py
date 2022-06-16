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
    
    @api.multi
    def import_characteristics(self):
        ids = self.env.context.get('active  _ids')
        if self.env['octopart.api'].check_api_key():
            for id in ids:
                category_rc = self.env['octopart.category'].search([('id', '=', id)])
                search_result = self.env['octopart.api'].get_data(self._set_data(category_rc.uid))
                if search_result and len(search_result['data']['categories']) > 0:
                    attributes = search_result['data']['categories'][0]['relevant_attributes']        
                    for attribute in attributes:
                        self._characteristics_management(attribute, id)    
            return True
        return False
    

    #Méthode pour le création ou la modification des characteristic
    def _characteristics_management(self, current_attributs, current_id):
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
    def _set_data(self, current_id):
        ids = [str(current_id)]
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