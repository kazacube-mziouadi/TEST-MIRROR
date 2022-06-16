# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
import openerp.addons.decimal_precision as dp
from docutils.nodes import field
from openerp.exceptions import ValidationError
import json
import urllib
import urllib2


class octopart_api(models.Transient):
    _name = 'octopart.api'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    apiKey = fields.Char(compute='_compute_apiKey')
    
    def _compute_apiKey(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', ''), ])
        if search_api_key:
            self.apiKey = search_api_key[0].octopart_api_key

    def check_api_key(self):
        if not self.apiKey:
            raise ValidationError(_("You do not have a key to connect to Octopart.")) 
        return True
       
    def get_data(self,data_to_send):
        if self.check_api_key():
            res = self._send_request_V4(data_to_send)
            if res:
                search_result = json.loads(res)      
                #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
                if 'errors' in search_result.keys():            
                    raise ValidationError(search_result['errors'][0]['message'])   
                return search_result
        
        return False

    def _send_request_V4(self, data_to_send):
        url = 'https://octopart.com/api/v4/endpoint'
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        headers['token'] = '{}'.format(self.apiKey)
        req = urllib2.Request(url, json.dumps(data_to_send).encode('utf-8'), headers)
        try:
            response = urllib2.urlopen(req)
            return response.read().decode('utf-8')
        except urllib2.HTTPError as e:
            print((e.read()))
            print('')
            raise e