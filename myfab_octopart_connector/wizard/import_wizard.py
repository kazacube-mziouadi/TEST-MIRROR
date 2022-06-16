# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
import openerp.addons.decimal_precision as dp
from openerp.addons.base_openprod.common import get_form_view
import json
import urllib
import urllib2
import base64
import requests
from datetime import datetime

class import_wizard_template(models.TransientModel):
    _name = 'connector.import.wizard.template'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    product_id = fields.Many2one('connector.result', string="Product")
    name = fields.Char(required=True)
    code_product = fields.Char(default=lambda self: self.env['ir.sequence'].get('product.product'), required=True)
    datasheet = fields.Char(string="Datasheet")
    image = fields.Char(string="Image")
    part_uid_octopart = fields.Char(required=True)
    manufacturer_name = fields.Char(string="Manufacturer name")
    manufacturer_uid_octopart = fields.Char(string="Manufacturer Octopart id")
    manufacturer_code = fields.Char(string="Manufacturer code")
    manufacturer_url = fields.Char(string="Manufacturer url")
    list_seller_offers_ids = fields.One2many('sellers.offers', 'import_wizard_template_id', string='Offers')
    product_template_id = fields.Many2one('product.product', 'Product template', required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', required=True, ondelete='restrict', default=lambda self: self.env.user.company_id)
    uop_id = fields.Many2one('product.uom', string='UoP',required=True, ondelete='restrict', help='Unit of Purchase')
    uoi_id = fields.Many2one('product.uom', string='UoI',required=True, ondelete='restrict', help='Unit of Invoice')
    directory_id = fields.Many2one('document.directory', string='Directory', required=True, ondelete='set null')
    apiKey = fields.Char(compute='_compute_apiKey')
    
    @api.one
    def _compute_apiKey(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        if search_api_key:
            self.apiKey = search_api_key[0].octopart_api_key

    @api.onchange('product_template_id')
    def _onchange_categ_id(self):
        if self.product_template_id:
            if self.product_template_id.uom_id:
                self.uop_id = self.product_template_id.uom_id.id
                self.uoi_id = self.product_template_id.uom_id.id
            
            if self.product_template_id.company_id:
                self.company_id = self.product_template_id.company_id.id

    @api.multi
    def import_product_template_wizard(self):
        search_result = self.env['connector.result'].browse(self.env.context.get('active_id'))
        
        # Convert image and datasheet to correct format
        photo = False
        if self.image:
            photo = base64.b64encode(requests.get(self.image).content)
        
        file_datasheet = False
        if self.datasheet:
            file_datasheet = base64.b64encode(requests.get(self.datasheet).content)
        
        # Check if manufacturer is already in openprod
        search_manufacturer = self.env['octopart.manufacturer'].search([['octopart_uid', '=', self.manufacturer_uid_octopart], ])
        if search_manufacturer:
            id_manufacturer = search_manufacturer[0].id
        else:
            
            # Create manufacturer
            add_manufacturer  = self.env['octopart.manufacturer'].create({
                'name' : self.manufacturer_name,
                'octopart_uid' : self.manufacturer_uid_octopart,
                'homepage_url' : self.manufacturer_url,
                          
            })
            id_manufacturer = add_manufacturer.id
            
        # Create new product
        new_product_rc = self.product_template_id.with_context(copy_by_button=True).copy({'name': self.name, 
                                                                                          'code': self.code_product, 
                                                                                          'octopart_uid_product': self.part_uid_octopart, 
                                                                                          'picture': photo, 
                                                                                          'manufacturer_id' : id_manufacturer,
                                                                                          'manufacturer_code' : self.manufacturer_code,
                                                                                          })
        
        # Create attachement for datasheet
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

        add_datasheet  = self.env['document.openprod'].create({
            'name' : 'datasheet-%s'%date_time,
            'extension' : 'pdf',
            'fname' : self.part_uid_octopart,
            'attachment' : file_datasheet,
            'version' : '1',
            'directory_id' : self.directory_id.id,
                      
        })
        # Add datasheet to product
        new_product_rc.write({'internal_plan_ids': [(4, add_datasheet.id, False)]})

        for offer in self.list_seller_offers_ids:
            # Check if seller is in openprod
            partner = self.env['res.partner'].search([['octopart_uid_seller', '=', offer.seller_identifier], ])
            search_currency = self.env['res.currency'].search([['name', '=', offer.list_price_ids[0].currency], ])
            if len(search_currency) > 0 and len(partner)>0:
                # Create a seller offer for the product
                add_seller_offer  = self.env['product.supplierinfo'].create({
                                'product_id' : new_product_rc.id,
                                'partner_id' : partner[0].id,
                                'currency_id' : search_currency[0].id,
                                'company_id' : self.company_id.id,
                                'uop_id' : self.uop_id.id,
                                'uoi_id' : self.uoi_id.id,
                                'supp_product_code' : offer.sku,
                                'delivery_delay' : offer.oder_delay,
                            })
                for price_offer in offer.list_price_ids: 
                    #  Create price for the offer
                    add_price = self.env['pricelist.supplierinfo'].create({
                        'sinfo_id' : add_seller_offer.id,
                        'min_qty' : price_offer.number_item,
                        'price' : price_offer.price,
                    })
        search_result.write({'is_in_openprod' : True})
        
        for characteristic in self.product_id.value_ids:
            # Add characteristic to product
            characteristic.write({'product_id' : new_product_rc.id})
            characteristic.write({'result_id' : None})

        self.write({'product_id' : False})
        return True

    @api.multi
    def import_details(self):
        #API request
        res = self.request_values_v4()
        
        #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
        if 'errors' in res.keys():            
            raise ValidationError(res['errors'][0]['message'])
        
        search_response = res['data']['parts'][0]
        currency_octopart = ''
        price_octopart = ''
        item_number = ''
        
        # Write request result to wizard
        url_datasheet = False
        url_image = False
        if 'sellers' in search_response:
            sellers = search_response['sellers']
        if search_response['best_datasheet'] != None:
            if 'url' in search_response['best_datasheet']:
                url_datasheet = search_response['best_datasheet']['url']
        if len(search_response['images']) > 0 and 'url' in search_response['images'][0]:
            url_image = search_response['images'][0]['url']
        
        self.write({
            'datasheet' : url_datasheet,
            'image' : url_image,
            'manufacturer_name' : search_response['manufacturer']['name'],
            'manufacturer_uid_octopart' : search_response['manufacturer']['id'],
            'manufacturer_url' : search_response['manufacturer']['homepage_url'],
            })
        for seller in sellers:
            # Check if seller is in openprod
            search_value = self.env['res.partner'].search_count([['octopart_uid_seller', '=', int(seller['company']['id'])], ])
            if search_value > 0:
                company_value = seller['company']                 
                for offer in seller['offers']:
                    # Check if order delay exist
                    if offer['factory_lead_days']:
                        order_delay_total = int(offer['factory_lead_days'])
                        week_number = order_delay_total // 7
                        order_delay = week_number * 5 + order_delay_total%7
                    else:
                        order_delay = None
                    add_seller_offer  = self.env['sellers.offers'].create({
                        'name' :company_value['name'], 
                        'seller_identifier' : company_value['id'], 
                        'sku' : offer['sku'],
                        #'octopart_currency' : currency_octopart,
                        'oder_delay' : order_delay,
                        'import_wizard_template_id' : self.id
                    })
                    # Create seller offer in wizard
                    for price in offer['prices']:
                        # Create price offer in wizard
                        add_price_offer  = self.env['price.offer'].create({
                            'offer_id' : add_seller_offer.id,
                            'currency' : price['currency'],
                            'price' : price['price'],
                            'number_item' : price['quantity']
                        })
                add_seller_offer.refresh()

        return {
            'type': 'ir.actions.act_window_no_close'
        }


    #Méthode pour l'envoie de requète
    def request_values_v4(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        apikey = search_api_key[0].octopart_api_key
        if apikey:
            res = self.send_V4(apikey)
            return json.loads(res)
        else:
            raise Warning(_("You do not have a key to connect to Octopart.")) 
    
      
    #méthode envoie et récupération de donnée serveur
    def send_V4(self, apikey):
        ids = [str(self.part_uid_octopart)]
        variables = {'ids': ids}
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
        query Part_Search($ids:[String!]!) {
          parts(ids: $ids, country:"", currency:"", distributorapi_timeout:"3"){
            best_datasheet{
              url
            }
            images{
              url
            }
            sellers(authorized_only :true, include_brokers:false, ){
              company{
                id
                name
              }
              offers{
                prices{
                  currency
                  quantity
                  price
                }
                sku
                factory_lead_days
                moq
                inventory_level 
              }
            }
            manufacturer{
              name
              id
                homepage_url
            }
          }
        }
        
        '''
        return query


class sellers_offers(models.TransientModel):
    _name = 'sellers.offers'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    import_wizard_template_id = fields.Many2one('connector.import.wizard.template', ondelte='cascade')
    add_price_id = fields.Many2one('add.octopart.price', ondelte='cascade')
    name = fields.Char(string="Name")
    seller_identifier = fields.Char(string="Seller")
    sku = fields.Char(String="Sku")
    eligible_region = fields.Char()
    #octopart_currency = fields.Char()
    oder_delay = fields.Integer(string="Order delay")
    list_price_ids = fields.One2many('price.offer', 'offer_id', string='List of prices')
    
    @api.multi
    def add_price(self):
        partner = self.env['res.partner'].search([['octopart_uid_seller', '=', self.seller_identifier], ])
        search_currency = self.env['res.currency'].search([['name', '=', self.list_price_ids[0].currency], ])
        if len(partner)>0 and len(search_currency)>0:
            add_seller_offer  = self.env['product.supplierinfo'].create({
                            'product_id' : self.add_price_id.product_id,
                            'partner_id' : partner[0].id,
                            'currency_id' : search_currency[0].id,
                            'company_id' : self.add_price_id.company_id.id,
                            'uop_id' : self.add_price_id.uop_id.id,
                            'uoi_id' : self.add_price_id.uoi_id.id,
                        })
            for price_offer in self.list_price_ids: 
                 
                add_price = self.env['pricelist.supplierinfo'].create({
                    'sinfo_id' : add_seller_offer.id,
                    'min_qty' : price_offer.number_item,
                    'price' : price_offer.price,
                })
        
        return True

class price_offer(models.TransientModel):
    _name = 'price.offer'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    offer_id = fields.Many2one('sellers.offers', required=True, ondelete='cascade')
    price = fields.Char()
    currency = fields.Char(string="Currency")
    number_item = fields.Char(string='Minimum order quantity')
