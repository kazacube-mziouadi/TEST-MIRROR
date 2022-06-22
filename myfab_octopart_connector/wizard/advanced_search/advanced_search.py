# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from bs4 import element
import json


class octopart_characteristic_filter(models.TransientModel):
    _name = 'octopart.characteristic.filter'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    research_id = fields.Many2one('octopart.product.research', required=True, ondelete='cascade', string="Research")
    category_id = fields.Many2one('octopart.category', required=True, ondelete='cascade', string="Octopart category")
    characteristic_type_id = fields.Many2one('characteristic.type', required=True, domain="[('octopart_category_ids', 'in', [category_id])]", string="Characteristic type")
    is_numerical_value = fields.Boolean(default=True)
    min_value = fields.Float(readonly=True, help="The minimum value of this attribute.")
    max_value = fields.Float(readonly=True, help="The maximum value of this attribute.")
    min_value_choose = fields.Float(help="The minimum value chosen for this attribute.")
    max_value_choose = fields.Float(help="The maximum value chosen for this attribute.")
    possible_values_ids = fields.One2many('octopart.characteristic.value.filter', 'characteristic_filter_id', string='Possible values')

    
    @api.onchange('category_id')
    def _onchange_warning_category_id(self):
        """
            Check if a categori was select in Octopart connector
        """
        res = {}
        if not self.category_id:
            res['warning'] = {'title':_('Warning'), 'message':_('You must first select a least one Octopart category')}
            self.category_id = False
        
        return res


    @api.onchange('characteristic_type_id')
    def _onchange_characteristics(self):
        res = {}
        if self.research_id and not self.research_id.category_id:
            res['warning'] = {'title':_('Warning'), 'message':_('You must first select a least one Octopart category')}
            self.category_id = False
        
        if self.characteristic_type_id:
            return self._show_characteristic_values()
        return res
            
    def _show_characteristic_values(self):
        if self.characteristic_type_id:
            # Make sure that all previous octopart.characteristic.value.filter have been deleted
            #erase = self.env['octopart.characteristic.value.filter'].search([])
            #erase.unlink()
            
            self.name = self.characteristic_type_id.name
            datas = self._request_characteristic_values()
            
            #On récupère les possible erreur et on les fais remonter
            if 'warning' in datas:
                return datas
            
            res = datas['buckets']
            value_added = []
            # Create a octopart.characteristic.value.filter for each value associated to the given characteristic type
            result = []
            for value in res:
                if value['float_value'] != None:
                    self.is_numerical_value = True
                    self.max_value = datas['max']
                    self.min_value = datas['min']
                    result_value = {
                        'characteristic_filter_id' : self.id, 
                        'characteristic_value' : value['float_value'],
                        'unit_value' : self.characteristic_type_id.unit_octopart,
                        'research_id' : self.research_id.id,
                    }
                else:
                    self.is_numerical_value = False
                    result_value = { 
                        'characteristic_filter_id' : self.id, 
                        'characteristic_value': value['display_value'],
                        'string_value' : True,
                        'unit_value' : self.characteristic_type_id.unit_octopart,
                        'research_id' : self.research_id.id,
                    }
                result.append((0, 0, result_value))
                
            self.possible_values_ids = result
        return {
            'type': 'ir.actions.act_window_no_close'
        }
        
    #Méthode pour l'envoie de requète
    def _request_characteristic_values(self):
        search_result = self.env['octopart.api'].get_api_data(self._set_data())
        if search_result:
            aggs = search_result['data']['search']['spec_aggs'][0]
            return aggs
        return False           
    
    #méthode envoie et récupération de donnée serveur
    def _set_data(self):
        ids = [str(self.category_id.octopart_uid)]
        attrs = []
        for attr in self.characteristic_type_id:
            attrs.append(str(attr.octopart_key))
        variables = {'ids': ids, 'attrs': attrs}
        data = {'query': self._query_def(),
                'variables': variables}
        return data
       
    #construtction de la requête 
    def _query_def(self):
        query ='''
        query Query_values($ids: [String!]!, $attrs: [String!]!){
          search(filters:{category_id: $ids}, in_stock_only:true) {
            spec_aggs(attribute_names: $attrs){
              attribute{
                id
                shortname
                name
              }
              buckets{
                display_value
                float_value
                count
              }
              min
              display_min
              max
              display_max
            }
          }                
        }
        
        '''
        return query
      
    @api.multi
    def add_characteristic_filter(self):
        filter_list = []
        is_use_value = False
        search_result = self.env['octopart.research.result'].browse(self.env.context.get('active_id'))
        # Create filter with selected value in wizard
        for element in self.possible_values_ids:
            if element.use_value == True:
                is_use_value = True
                name_filter = self.characteristic_type_id.name
                value_type = False
                if element.string_value:
                    value_type = True
                add_name = " = %s" % element.characteristic_value
                name_filter = name_filter + add_name
                values =  {
                            'name' : name_filter,
                            'metadata_key' : self.characteristic_type_id.octopart_key,
                            'search_id' : search_result.id,
                            'characteristic_value' : element.characteristic_value,
                            'string_value' : value_type,
                        }
                
                filter_list.append(self.env['octopart.characteristics.research'].create(values).id)
        # Set the upper and lower limit of specification
        if self.is_numerical_value and not is_use_value:
            if self.min_value_choose or self.max_value_choose:
                add_characteristic_filter = False
                name_filter = self.characteristic_type_id.name
                if self.min_value_choose :
                    add_name = ", >=%f" % self.min_value_choose
                    name_filter = name_filter+add_name
                    add_characteristic_filter = True
                if self.max_value_choose :
                    add_name = ", <=%f" % self.max_value_choose
                    name_filter = name_filter+add_name
                    add_characteristic_filter = True
                
                if add_characteristic_filter:
                    values =  {
                        'name' : name_filter,
                        'metadata_key' : self.characteristic_type_id.octopart_key,
                        'search_id' : search_result.id,
                        'min_value_choose' : self.min_value_choose,
                        'max_value_choose' : self.max_value_choose
                    }
                    
                    filter_list.append(self.env['octopart.characteristics.research'].create(values).id)
            
        for filter_id in filter_list:
            self.research_id.write({'characteristics_filter_ids': [(4, filter_id, 0)]})
            
        self.possible_values_ids.unlink()
        
    
class octopart_characteristic_value_filter(models.TransientModel):
    _name = 'octopart.characteristic.value.filter'
    _description = 'Characteristic values used by filter'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char()
    research_id = fields.Many2one('octopart.product.research', ondelete='cascade')
    characteristic_filter_id = fields.Many2one('octopart.characteristic.filter', required=True, ondelete='cascade')
    string_value = fields.Boolean(default = False)
    characteristic_value = fields.Char(string="Value")
    unit_value = fields.Char(string="Unit")
    use_value = fields.Boolean()
 