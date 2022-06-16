# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from bs4 import element
import json
import urllib
import urllib2


class advanced_search(models.TransientModel):
    _name = 'connector.advanced.search'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    category_id = fields.Many2one('octopart.category', required=True, ondelete='cascade')
    add_characteristics_type_id = fields.Many2one('characteristic.type', required=True, domain="[('octopart_category_ids', 'in', [category_id])]")
    spec_min_value = fields.Float(string="Minimum value choose", help="The minimum value chosen for this attribute.")
    min_value = fields.Float(string="Minimum value", readonly=True, help="The minimum value of this attribute")
    spec_max_value = fields.Float(string="Maximum value choose", help="The maximum value chosen for this attribute.")
    max_value = fields.Float(string="Maximum value", readonly=True, help="The maximum value of this attribute")
    list_possible_values_ids = fields.One2many('specs.value.search', 'search_id', string='Possible values')
    active_connector_id = fields.Many2one('connector.product', required=True, ondelete='cascade')
    is_numerical_value = fields.Boolean(default=True)

    
    @api.onchange('category_id')
    def _onchange_warning_category_id(self):
        """
            Check if a categori was select in Octopart connector
        """
        res = {}
        if not self.category_id:
            res['warning'] = {'title':_('Warning'), 'message':_('You must first select a category in Octopart connector')}
            self.category_id = False
        
        return res


    @api.onchange('add_characteristics_type_id')
    def _onchange_characteristics(self):
        res = {}
        if self.active_connector_id and not self.active_connector_id.category_id:
            res['warning'] = {'title':_('Warning'), 'message':_('You must first select a category in Octopart connector')}
            self.category_id = False
        
        if self.add_characteristics_type_id:
            return self.show_spec_value()
        return res
            

    @api.multi
    def show_spec_value(self):
        if self.add_characteristics_type_id:
            # Make sure that all previous specs.value.search have been deleted
            #erase = self.env['specs.value.search'].search([])
            #erase.unlink()
            
            self.name = self.add_characteristics_type_id.name
            datas = self.request_values_v4()
            
            #On récupère les possible erreur et on les fais remonter
            if 'warning' in datas:
                return datas
            
            res = datas['buckets']
            value_added = []
            # Create a specs.value.search for each value associated to the given characteristic type
            result = []
            for value in res:
                if value['float_value'] != None:
                    self.is_numerical_value = True
                    self.max_value = datas['max']
                    self.min_value = datas['min']
                    result_value = {
                        'search_id' : self.id, 
                        'spec_value' : value['float_value'],
                        'unit_value' : self.add_characteristics_type_id.unit_octopart,
                        'connector_id' : self.active_connector_id.id,
                    }
                else:
                    self.is_numerical_value = False
                    result_value = { 
                        'search_id' : self.id, 
                        'spec_value': value['display_value'],
                        'string_value' : True,
                        'unit_value' : self.add_characteristics_type_id.unit_octopart,
                        'connector_id' : self.active_connector_id.id,
                    }
                result.append((0, 0, result_value))
                
            self.list_possible_values_ids = result
        return {
            'type': 'ir.actions.act_window_no_close'
        }
        
    #Méthode pour l'envoie de requète
    def request_values_v4(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        apikey = search_api_key[0].octopart_api_key
        if apikey:
            res = self.send_V4(apikey)
            search_result = json.loads(res)
        else:
            raise Warning(_("You do not have a key to connect to Octopart.")) 
        
        #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
        if 'errors' in search_result.keys():            
            res = {}
            res['warning'] = {'title':_('Warning'), 'message': search_result['errors'][0]['message']}
            return res
            
        aggs = search_result['data']['search']['spec_aggs'][0]
        return aggs   
    
      
    #méthode envoie et récupération de donnée serveur
    def send_V4(self, apikey):
        ids = [str(self.category_id.uid)]
        attrs = []
        for attr in self.add_characteristics_type_id:
            attrs.append(str(attr.octopart_key))
        variables = {'ids': ids, 'attrs': attrs}
        url = 'https://octopart.com/api/v4/endpoint'
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        headers['token'] = '{}'.format(apikey)
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
    def add_filter(self):
        filter_list = []
        is_use_value = False
        search_result = self.env['connector.result'].browse(self.env.context.get('active_id'))
        # Create filter with selected value in wizard
        for element in self.list_possible_values_ids:
            if element.use_value == True:
                is_use_value = True
                name_filter = self.add_characteristics_type_id.name
                value_type = False
                if element.string_value:
                    value_type = True
                add_name = " = %s" % element.spec_value
                name_filter = name_filter + add_name
                values =  {
                            'name' : name_filter,
                            'metedata_key' : self.add_characteristics_type_id.octopart_key,
                            'search_connector_id' : search_result.id,
                            'spec_value' : element.spec_value,
                            'string_value' : value_type,
                        }
                
                filter_list.append(self.env['specs.search'].create(values).id)
        # Set the upper and lower limit of specification
        if self.is_numerical_value and not is_use_value:
            if self.spec_min_value or self.spec_max_value:
                add_filter = False
                name_filter = self.add_characteristics_type_id.name
                if self.spec_min_value :
                    add_name = ", >=%f" % self.spec_min_value
                    name_filter = name_filter+add_name
                    add_filter = True
                if self.spec_max_value :
                    add_name = ", <=%f" % self.spec_max_value
                    name_filter = name_filter+add_name
                    add_filter = True
                
                if add_filter:
                    values =  {
                        'name' : name_filter,
                        'metedata_key' : self.add_characteristics_type_id.octopart_key,
                        'search_connector_id' : search_result.id,
                        'spec_min_value' : self.spec_min_value,
                        'spec_max_value' : self.spec_max_value
                    }
                    
                    filter_list.append(self.env['specs.search'].create(values).id)
            
        for filter_id in filter_list:
            self.active_connector_id.write({'list_specs_search_ids': [(4, filter_id, 0)]})
            
        self.list_possible_values_ids.unlink()
        
    
class specs_value_search(models.TransientModel):
    _name = 'specs.value.search'
    _description = 'List of value associated to a spec for the wizard'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(string="Name")
    search_id = fields.Many2one('connector.advanced.search', required=True, ondelete='cascade')
    string_value = fields.Boolean(string="String value", default = False)
    spec_value = fields.Char(string="Value")
    unit_value = fields.Char(string="Unit")
    use_value = fields.Boolean()
    connector_id = fields.Many2one('connector.product', ondelete='cascade')
 