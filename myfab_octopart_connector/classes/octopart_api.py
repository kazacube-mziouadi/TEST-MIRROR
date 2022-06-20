# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
import json
import urllib
import urllib2

class octopart_api(models.TransientModel):
    _name = 'octopart.api'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================    
    def _get_api_key(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', '')])
        if search_api_key:
            return search_api_key[0].octopart_api_key
        return False

    def check_api_key(self,raise_error=True):
        return self._check_api_key(self._get_api_key(),raise_error)
 
    def get_api_data(self,data_to_send):
        api_version = 4
        api_key = self._get_api_key()
        if self._check_api_key(api_key):
            res = self._send_request(api_version,api_key,data_to_send)
            if res:
                search_result = json.loads(res)      
                #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
                if 'errors' in search_result.keys():            
                    raise ValidationError(search_result['errors'][0]['message'])   
                return search_result
        
        return False

    def _check_api_key(self,api_key,raise_error=True):
        if not api_key:
            if raise_error:
                raise ValidationError(_("You do not have a key to connect to Octopart.")) 
            return False
        return True

    def _send_request(self, api_version, api_key, data_to_send):
        if self._check_api_key(api_key):
            if api_version == 4:
                return self._send_request_V4(api_key,data_to_send)

        return False

    def _send_request_V4(self, api_key, data_to_send):
        if not self._check_api_key(api_key):
            return False

        url = 'https://octopart.com/api/v4/endpoint'
        headers = {'Accept': 'application/json',
                'Content-Type': 'application/json'}
        headers['token'] = '{}'.format(api_key)
        req = urllib2.Request(url, json.dumps(data_to_send).encode('utf-8'), headers)
        try:
            response = urllib2.urlopen(req)
            return response.read().decode('utf-8')
        except urllib2.HTTPError as e:
            print((e.read()))
            print('')
            raise e