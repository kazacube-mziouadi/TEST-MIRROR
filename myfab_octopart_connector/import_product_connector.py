# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from docutils.nodes import field
from openerp.exceptions import ValidationError
import json
import urllib
import urllib2
import ast

class connector_product(models.Model):
    _name = 'connector.product'
    _description = 'Search product connector'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(string="Connector name", required=True, default='Connector Octopart')
    category_id = fields.Many2one('octopart.category', 'Category Octopart')
    brand_name = fields.Char()
    manufacturer_name = fields.Many2one('octopart.manufacturer', 'Manufacturer')
    seller_name = fields.Many2one('connector.seller', 'Seller')
    description = fields.Char(string="Description")
    list_result_ids = fields.One2many('connector.result', 'search_id', string='Result')
    list_specs_search_ids = fields.Many2many('specs.search', 'search_connector_id', string='Search filters', domain = "[('search_connector_id','=', active_id),]")
    result_number = fields.Integer(default=0)
    count_response = fields.Integer(default=0)
    sample = fields.Integer(string="Sample", default=10)
    apiKey = fields.Char(compute='_compute_apiKey')
    
    
    @api.one
    def _compute_apiKey(self):
        # Get api key from technical data config
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        if search_api_key:
            self.apiKey = search_api_key[0].octopart_api_key
    
        return True
   
    
    @api.multi
    def request_part(self):
        
        self.write({'count_response' : 0, 'result_number' : 0})
        self.list_result_ids.unlink()
        
        self.search_part()       
           
        return True
    
    
    @api.multi
    def more_result(self):
        
        if self.count_response<901:
            self.search_part()
        
        return True

    
    def search_part_v4(self, variables):
        #Test de connection serveur Octopart api V4
        url = 'https://octopart.com/api/v4/endpoint'
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        headers['token'] = '{}'.format(self.apiKey)
        data = {'query': self.get_search(),
                'variables': variables}
        req = urllib2.Request(url, json.dumps(data).encode('utf-8'), headers)
        try:
            response = urllib2.urlopen(req)
            return response.read().decode('utf-8')
        except urllib2.HTTPError as e:
            print((e.read()))
            print('')
            raise e
    
    
    def get_search(self):
        query='''
        query($q:String, $start: Int, $limit:Int ,$filters: Map){ 
            search(q: $q, start:$start, limit:$limit, filters:$filters){
                hits
                results {
                  part{
                    mpn
                    name
                    id
                    octopart_url
                    short_description
                    manufacturer{
                      name
                    }
                    specs{
                      attribute{
                        id
                        name
                        shortname
                      }
                      display_value
                    }
                  }
                }
            }
        }
        '''
        return query


    @api.multi
    def search_part(self):
        search_string = ""
        check_search_value = True
        result_ignored = 0
        list_specs_filter = {}
        variable = {}
                    
        # Add argument depending on fields value
        filter_args = {}
        if 'category_id' in self.env['connector.product']._fields:
            if self.category_id:
                filter_args['category_id'] = int(self.category_id.uid)
            
        if 'manufacturer_name' in self.env['connector.product']._fields:
            if self.manufacturer_name:
                filter_args['manufacturer_id'] = int(self.manufacturer_name.octopart_uid)

        if 'seller_name' in self.env['connector.product']._fields:
            if self.seller_name:
                seller_name = self.seller_name.name.replace('-', ' ')
                filter_args['sellers_id'] = int(self.seller_name.octopart_uid)
                
        if 'description' in self.env['connector.product']._fields:
            if self.description:
                variable['q'] = self.description

        # Check for advanced search filter       
        if 'list_specs_search_ids' in self.env['connector.product']._fields:
            if self.list_specs_search_ids:
                for element in self.list_specs_search_ids:
                    if element.spec_value:
                        if element.metedata_key not in list_specs_filter:
                            list_specs_filter[element.metedata_key] = []
                                
                        if element.spec_value:
                            list_specs_filter[element.metedata_key].append(element.spec_value)
                            
                    elif element.spec_min_value or element.spec_max_value:
                        if element.metedata_key not in list_specs_filter:
                            list_specs_filter[element.metedata_key] = []
                            
                        if element.spec_max_value and element.spec_min_value:
                            list_specs_filter[element.metedata_key].append('"('+str(element.spec_min_value)+'__'+str(element.spec_max_value)+')"')
                        elif element.spec_max_value:
                            list_specs_filter[element.metedata_key].append('"('+str(element.spec_min_value)+'__)"')
                        elif element.spec_min_value:
                            list_specs_filter[element.metedata_key].append('"(__'+str(element.spec_max_value)+')"')

                #api v4
                for spec in list_specs_filter:
                    is_string_value = False
                    try:
                        float(list_specs_filter[spec][0])
                    except:
                        is_string_value = True    
                    if is_string_value:
                        filter_args[spec] = list_specs_filter[spec]
                    else:
                        val_list = []
                        for val in list_specs_filter[spec]:
                            val_list.append(float(val))
                        filter_args[spec] = val_list

        variable['limit'] = self.sample
        variable['start'] = self.count_response
        variable['filters'] = filter_args
        
        if self.apiKey:
            res = self.search_part_v4(variable)
            search_result = json.loads(res)
        else:
            raise ValidationError(_("You do not have a key to connect to Octopart."))  

        #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
        if 'errors' in search_result.keys():            
            raise ValidationError(search_result['errors'][0]['message'])
        
        datas = search_result['data']['search']
        if self.count_response == 0:
            resultNumber = datas['hits']
        else:
            resultNumber = self.result_number
        parts = datas['results']    
        # Result from api request
        if parts:
            for part in parts:
                # Check if result respect advanced filter
                values = part['part']
                # Check if result is already an openprod product
                is_present = False
                search_product = self.env['product.product'].search_count([('octopart_uid_product', '=', values['id']), ])
                if search_product > 0 :
                    is_present = True
                # Create result in openprod
                active_result_rc  = self.env['connector.result'].create({
                    'search_id' : self.id,
                    'brand_name' : values['manufacturer']['name'],
                    'mnp' : values['mpn'],
                    'octopart_url' : values['octopart_url'],
                    'short_description' : values['short_description'],
                    'octopart_uid' : values['id'],
                    'is_in_openprod' : is_present,
                })
                    
                # Get specs from api request response
                specs = values['specs']
                for element in specs:
                    active_spec_rc = self.characteristics_manager(element['attribute'])
                        
                    if self.id not in active_spec_rc.octopart_category_ids.ids:
                        active_spec_rc.write({'octopart_category_ids' : [(4, self.id)],  })
                    # Get value from spec 
                    
                    # Check if value is already an openprod characteristic value
                    search_characteristic_value = self.env['characteristic.value'].search([('name', '=', element['display_value'])])
                    if search_characteristic_value:
                       active_value_rc = search_characteristic_value[0]
                    else:
                        # Create characteristic value
                        add_spec_value_octopart  = self.env['characteristic.value'].create({
                            'name' : element['display_value'],
                            'type_id' : active_spec_rc.id,   
                        }) 
                        active_value_rc = add_spec_value_octopart
                      
                    if self.id not in active_value_rc.octopart_category_ids.ids:  
                        active_value_rc.write({'octopart_category_ids' : [(4, self.id)],  })  
                    
                    unit_openprod = ""
                    search_unit_openprod = self.env['product.uom'].search([('name', '=', active_spec_rc.unit_octopart), ])
                    if search_unit_openprod:
                        unit_openprod = search_unit_openprod[0].id
                    #Create characteristic for result
                    add_characteristic = self.env['characteristic'].create({
                        'characteristic_type_id' : active_spec_rc.id,
                        'value' : active_value_rc.id,
                        'unit_octopart' : active_spec_rc.unit_octopart,
                        'uom_id' : unit_openprod,
                        'result_id' : active_result_rc.id,
                    })
                    active_result_rc.write({'value_ids' : [(4, add_characteristic.id)],    })
                                      
                        
        self.write({'count_response' : self.count_response + 10 })
        resultNumber = resultNumber-result_ignored
        self.write({'result_number' : resultNumber})
        
        return True
   
   
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
                
        return active_spec_rc
    
        
    @api.onchange('category_id', 'brand_name', 'seller_name', 'description', 'list_specs_search_ids')
    def _onchange_stop_more_result(self):
        self.write({'count_response' : 0 })
        
    
    
    @api.multi
    def clear_part(self):

        self.list_result_ids.unlink()
        self.write({'count_response' : 0})
        self.write({'result_number' : 0})        
        filters = self.list_specs_search_ids.search([('search_connector_id', '=', self.id), ])
        filters.unlink()   
           
        


class connector_result(models.Model):
    _name = 'connector.result'
    _description = 'Result from search product'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    search_id = fields.Many2one('connector.product',required=True, ondelete='cascade')
    brand_name = fields.Char()
    mnp = fields.Char()
    octopart_url = fields.Char()
    short_description = fields.Char()
    octopart_uid = fields.Char()
    is_in_openprod = fields.Boolean(default=False)
    value_ids = fields.Many2many('characteristic')
    
    
    @api.multi
    def open_sellers_offers(self):
        return {
            "type": "ir.actions.act_url",
            "url": self.octopart_url,
            "target": "new",
        }
    
    
class specs_search(models.Model):
    _name = 'specs.search'
    _description = 'Specs from Octopart'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    metedata_key = fields.Char(string="Octopart Key")
    name = fields.Char(string="Filter name")
    search_connector_id = fields.Many2one('connector.product',required=True, ondelete='cascade')
    spec_value = fields.Char(string="Value")
    string_value = fields.Boolean(string="String value", default=False)
    spec_min_value = fields.Float(string="Min value")
    spec_max_value = fields.Float(string="Max value")
      
        
class connector_seller(models.Model):
    _name = 'connector.seller'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(required=True)
    octopart_uid = fields.Char(required=True)
    homepage_url = fields.Char()
    display_flag = fields.Char()
    has_ecommerce = fields.Boolean()
    is_verified = fields.Boolean(string=" Is verified", default=False, help="True if a manufacturer participates in Octopart's Verified Manufacturer program.")
    is_distributorapi = fields.Boolean(string="Is distributor", default=False, help="rue if a distributor has an API integration with Octopart to provide latest pricing and stock data.")
        
        
class octopart_manufacturer(models.Model):
    _name = 'octopart.manufacturer'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char()
    octopart_uid = fields.Char()
    homepage_url = fields.Char()
    part_in_openprod = fields.Integer(compute='_compute_part_in_openprod')
    is_verified = fields.Boolean(string=" Is verified", default=False, help="True if a manufacturer participates in Octopart's Verified Manufacturer program.")
    is_distributorapi = fields.Boolean(string="Is distributor", default=False, help="rue if a distributor has an API integration with Octopart to provide latest pricing and stock data.")
    
    
    @api.one
    def _compute_part_in_openprod(self):
        search_part = self.env['product.product'].search_count([['manufacturer_id', '=', self.id], ])
        self.part_in_openprod = search_part
        
        return True
