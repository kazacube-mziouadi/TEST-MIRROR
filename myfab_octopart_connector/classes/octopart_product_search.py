# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import json
import ast

class octopart_product(models.Model):
    _name = 'octopart.product'
    _description = 'Search product on Octopart'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(string="Connector name", required=True, default='Connector Octopart')
    category_id = fields.Many2one('octopart.category', 'Category Octopart')
    brand_name = fields.Char()
    manufacturer_name = fields.Many2one('octopart.manufacturer', 'Manufacturer')
    seller_name = fields.Many2one('octopart.seller', 'Seller')
    description = fields.Char(string="Description")
    list_result_ids = fields.One2many('octopart.search.result', 'search_id', string='Result')
    list_specs_search_ids = fields.Many2many('octopart.specs.search', 'search_connector_id', string='Search filters', domain = "[('search_connector_id','=', active_id),]")
    result_number = fields.Integer(default=0)
    count_response = fields.Integer(default=0)
    sample = fields.Integer(string="Sample", default=10)  
    
    @api.onchange('category_id', 'brand_name', 'seller_name', 'description', 'list_specs_search_ids')
    def _onchange_stop_more_result(self): 
        self.write({'count_response' : 0 })

    @api.one
    def search_product(self):
        self.clear_result()
        self._search_product()       
        return True
    
    @api.one
    def more_product_results(self):
        if self.count_response <= self.result_number and self.count_response < 901:
            self._search_product()
        return True

    @api.one
    def clear_result(self):
        self.list_result_ids.unlink()
        self._set_count_and_results(0,0)    
        filters = self.list_specs_search_ids.search([('search_connector_id', '=', self.id), ])
        filters.unlink() 

    def _search_product(self):
        if count_response >= resultNumber:
            return True

        variable = {}
                    
        # Add argument depending on fields value
        if 'description' in self.env['octopart.product']._fields and self.description:
            variable['q'] = self.description

        variable['limit'] = self.sample
        variable['start'] = self.count_response
        variable['filters'] = self._get_filter()
        
        search_result = self.env['octopart.api'].get_api_data(self._set_data(variable))
        if search_result:
            datas = search_result['data']['search']
            if self.count_response == 0:
                resultNumber = datas['hits']
            else:
                resultNumber = self.result_number

            self._parts_management(datas['results'])

            count_response = self.count_response + self.sample
            if count_response > resultNumber:
                count_response = resultNumber
            self._set_count_and_results(count_response, resultNumber)
        
        return True

    def _get_filter(self):
        filter_args = {}
        if 'category_id' in self.env['octopart.product']._fields and self.category_id:
            filter_args['category_id'] = int(self.category_id.uid)
            
        if 'manufacturer_name' in self.env['octopart.product']._fields and self.manufacturer_name:
            filter_args['manufacturer_id'] = int(self.manufacturer_name.octopart_uid)

        if 'seller_name' in self.env['octopart.product']._fields and self.seller_name:
            seller_name = self.seller_name.name.replace('-', ' ')
            filter_args['sellers_id'] = int(self.seller_name.octopart_uid)

        # Check for advanced search filter       
        if 'list_specs_search_ids' in self.env['octopart.product']._fields and self.list_specs_search_ids:
            #api v4
            list_specs_filter = self._get_spec_filter()
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
            
        return filter_args

    def _get_spec_filter(self):
        list_specs_filter = {}
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
        
        return list_specs_filter

    def _parts_management(self, parts):
        # Result from api request
        if parts:
            for part in parts:
                # Check if result respect advanced filter
                values = part['part']
                # Create result in openprod
                active_result_rc  = self.env['octopart.search.result'].create({
                    'search_id' : self.id,
                    'brand_name' : values['manufacturer']['name'],
                    'mpn' : values['mpn'],
                    'octopart_url' : values['octopart_url'],
                    'short_description' : values['short_description'],
                    'octopart_uid' : values['id']
                })
                    
                # Get specs from api request response
                self._specs_management(active_result_rc, values['specs'])

    def _specs_management(self, active_result_rc, specs):
        if specs:
            for element in specs:
                active_spec_rc = self._characteristics_management(element['attribute'])
                    
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

    def _characteristics_management(self, current_attributs):
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
    
    def _set_count_and_results(self,count_response,resultNumber):
        self.write({'count_response' : count_response })
        self.write({'result_number' : resultNumber})

    def _set_data(self, variables):
        #Test de connection serveur Octopart api V4
        data = {'query': self._query_def(),
                'variables': variables}
        return data
    
    
    def _query_def(self):
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

class octopart_specs_search(models.Model):
    _name = 'octopart.specs.search'
    _description = 'Specs from Octopart'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    metedata_key = fields.Char(string="Octopart Key")
    name = fields.Char(string="Filter name")
    search_connector_id = fields.Many2one('octopart.product',required=True, ondelete='cascade')
    string_value = fields.Boolean(string="String value", default=False)
    spec_value = fields.Char(string="Value")
    spec_min_value = fields.Float(string="Min value")
    spec_max_value = fields.Float(string="Max value")

class octopart_search_result(models.Model):
    _name = 'octopart.search.result'
    _description = 'Result from search product'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    search_id = fields.Many2one('octopart.product',required=True, ondelete='cascade')
    octopart_uid = fields.Char()
    brand_name = fields.Char()
    mpn = fields.Char(string="Manufacturer code")
    octopart_url = fields.Char()
    short_description = fields.Char()
    value_ids = fields.Many2many('characteristic')
    is_in_openprod = fields.Boolean(compute='_compute_in_openprod')
    
    def _compute_in_openprod(self):
        if self.env['product.product'].search([['octopart_uid_product', '=', self.octopart_uid], ]):
            self.is_in_openprod = True
        else:
            self.is_in_openprod = False
        
        return True
    
    @api.multi
    def open_sellers_offers(self):
        return {
            "type": "ir.actions.act_url",
            "url": self.octopart_url,
            "target": "new",
        }