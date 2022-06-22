# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import json
import ast

class octopart_product_research(models.Model):
    _name = 'octopart.product.research'
    _description = 'Search product on Octopart'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(string="Research name", required=True, default=_('Octopart search'))
    description = fields.Char()
    category_id = fields.Many2one('octopart.category', 'Octopart Category')
    manufacturer_id = fields.Many2one('octopart.manufacturer', 'Octopart Manufacturer')
    seller_id = fields.Many2one('octopart.seller', 'Octopart Seller')
    sample = fields.Integer(default=10)  
    characteristics_filter_ids = fields.Many2many('octopart.characteristics.research', 'search_id', string='Characteristics filters', domain = "[('search_id','=', active_id),]")
    number_of_results = fields.Integer(default=0)
    number_of_results_readed = fields.Integer(default=0)
    result_ids = fields.One2many('octopart.research.result', 'search_id', string='Result')
    
    @api.onchange('category_id', 'seller_id', 'description', 'characteristics_filter_ids')
    def _onchange_stop_more_result(self): 
        self.write({'number_of_results_readed' : 0 })

    @api.one
    def search_product(self):
        self.clear_result()
        self._search_product()       
        return True
    
    @api.one
    def more_product_results(self):
        if self.number_of_results_readed <= self.number_of_results and self.number_of_results_readed < 901:
            self._search_product()
        return True

    @api.one
    def clear_result(self):
        self.result_ids.unlink()
        self._set_number_of_results(0,0)    
        filters = self.characteristics_filter_ids.search([('search_id', '=', self.id), ])
        filters.unlink() 

    def _search_product(self):
        if self.number_of_results_readed > 0 and self.number_of_results_readed >= self.number_of_results:
            return True

        variable = {}
                    
        # Add argument depending on fields value
        if 'description' in self.env['octopart.product.research']._fields and self.description:
            variable['q'] = self.description

        variable['limit'] = self.sample
        variable['start'] = self.number_of_results_readed
        variable['filters'] = self._get_filter()

        search_result = self.env['octopart.api'].get_api_data(self._set_data(variable))
        if search_result:
            datas = search_result['data']['search']
            if self.number_of_results_readed == 0:
                number_of_results = datas['hits']
            else:
                number_of_results = self.number_of_results

            self._product_management(datas['results'])

            number_of_results_readed = self.number_of_results_readed + self.sample
            if number_of_results_readed > number_of_results:
                number_of_results_readed = number_of_results
            self._set_number_of_results(number_of_results_readed, number_of_results)
        
        return True

    def _get_filter(self):
        filter_args = {}
        if 'category_id' in self.env['octopart.product.research']._fields and self.category_id:
            filter_args['category_id'] = int(self.category_id.octopart_uid)
            
        if 'manufacturer_id' in self.env['octopart.product.research']._fields and self.manufacturer_id:
            filter_args['manufacturer_id'] = int(self.manufacturer_name.octopart_uid)

        if 'seller_id' in self.env['octopart.product.research']._fields and self.seller_id:
            seller_id = self.seller_id.name.replace('-', ' ')
            filter_args['sellers_id'] = int(self.seller_id.octopart_uid)

        # Check for advanced search filter       
        if 'characteristics_filter_ids' in self.env['octopart.product.research']._fields and self.characteristics_filter_ids:
            #api v4
            list_specs_filter = self._get_characteristic_filter()
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

    def _get_characteristic_filter(self):
        list_specs_filter = {}
        for element in self.characteristics_filter_ids:
            if element.characteristic_value:
                if element.metadata_key not in list_specs_filter:
                    list_specs_filter[element.metadata_key] = []  

                if element.characteristic_value:
                    list_specs_filter[element.metadata_key].append(element.characteristic_value)
                    
            elif element.min_value_choose or element.max_value_choose:
                if element.metadata_key not in list_specs_filter:
                    list_specs_filter[element.metadata_key] = []
                    
                if element.max_value_choose and element.min_value_choose:
                    list_specs_filter[element.metadata_key].append('"('+str(element.min_value_choose)+'__'+str(element.max_value_choose)+')"')
                elif element.max_value_choose:
                    list_specs_filter[element.metadata_key].append('"('+str(element.min_value_choose)+'__)"')
                elif element.min_value_choose:
                    list_specs_filter[element.metadata_key].append('"(__'+str(element.max_value_choose)+')"')
        
        return list_specs_filter

    def _product_management(self, parts):
        # Result from api request
        if parts:
            for part in parts:
                # Check if result respect advanced filter
                values = part['part']
                # Create result in openprod
                active_result_rc  = self.env['octopart.research.result'].create({
                    'search_id' : self.id,
                    'brand_name' : values['manufacturer']['name'],
                    'mpn' : values['mpn'],
                    'octopart_url' : values['octopart_url'],
                    'short_description' : values['short_description'],
                    'octopart_uid' : values['id']
                })
                    
                # Get specs from api request response
                self._characteristics_management(active_result_rc, values['specs'])

    def _characteristics_management(self, active_result_rc, specs):
        if specs:
            for element in specs:
                active_spec_category_rc = self.env['octopart.category'].characteristics_management(self.id, element['attribute'])
                    
                if self.id not in active_spec_category_rc.octopart_category_ids.ids:
                    active_spec_category_rc.write({'octopart_category_ids' : [(4, self.id)],  })
                # Get value from spec 
                
                # Check if value is already an openprod characteristic value
                search_characteristic_value = self.env['characteristic.value'].search([('name', '=', element['display_value'])])
                if search_characteristic_value:
                    active_value_rc = search_characteristic_value[0]
                else:
                    # Create characteristic value
                    active_value_rc = self.env['characteristic.value'].create({
                        'name' : element['display_value'],
                        'type_id' : active_spec_category_rc.id,   
                    }) 
                
                if self.id not in active_value_rc.octopart_category_ids.ids:  
                    active_value_rc.write({'octopart_category_ids' : [(4, self.id)],})  
                
                unit_openprod = ""
                search_unit_openprod = self.env['product.uom'].search([('name', '=', active_spec_category_rc.unit_octopart), ])
                if search_unit_openprod:
                    unit_openprod = search_unit_openprod[0].id

                #Create characteristic for result
                add_characteristic = self.env['characteristic'].create({
                    'characteristic_type_id' : active_spec_category_rc.id,
                    'value' : active_value_rc.id,
                    'unit_octopart' : active_spec_category_rc.unit_octopart,
                    'uom_id' : unit_openprod,
                    'result_id' : active_result_rc.id,
                })
                active_result_rc.write({'value_ids' : [(4, add_characteristic.id)],})
    
    def _set_number_of_results(self,number_of_results_readed,number_of_results):
        self.write({'number_of_results' : number_of_results})
        self.write({'number_of_results_readed' : number_of_results_readed })

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

class octopart_characteristics_research(models.Model):
    _name = 'octopart.characteristics.research'
    _description = 'Octopart characteristics research'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char(string="Filter name")
    search_id = fields.Many2one('octopart.product.research',required=True, ondelete='cascade')
    metadata_key = fields.Char(string="Octopart Key")
    string_value = fields.Boolean(default=False)
    characteristic_value = fields.Char(string="Value")
    min_value_choose = fields.Float(string="Min value")
    max_value_choose = fields.Float(string="Max value")

class octopart_research_result(models.Model):
    _name = 'octopart.research.result'
    _description = 'Result Octopart product search'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    search_id = fields.Many2one('octopart.product.research',required=True, ondelete='cascade')
    octopart_uid = fields.Char()
    brand_name = fields.Char()
    mpn = fields.Char(string="Manufacturer code")
    octopart_url = fields.Char()
    short_description = fields.Char()
    value_ids = fields.Many2many('characteristic')
    is_in_openprod = fields.Boolean(compute='_compute_is_in_openprod')
    
    def _compute_is_in_openprod(self):
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