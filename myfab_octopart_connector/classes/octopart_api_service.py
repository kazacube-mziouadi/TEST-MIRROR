# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
import json
import urllib
import urllib2
import logging

logger = logging.getLogger(__name__)
API_VERSION = 4

class octopart_api_service(models.TransientModel):
    _name = 'octopart.api.service'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================    
    def _get_api_key(self):
        search_api_key = self.env['technical.data.config.settings'].search([('octopart_api_key', '!=', '')])
        if search_api_key:
            return search_api_key[0].octopart_api_key
        return False

    def is_api_key_valid(self,raise_error=True):
        return self._is_api_key_valid(self._get_api_key(),raise_error)
 
    def get_api_data(self,request_body):
        api_key = self._get_api_key()
        if self._is_api_key_valid(api_key):
            res = self._send_request(API_VERSION,api_key,request_body)
            if res:
                search_result = json.loads(res)      
                #On vérifie si octopart a renvoyer une erreur et dans ce cas on l'affiche
                if 'errors' in search_result.keys():            
                    raise ValidationError(search_result['errors'][0]['message'])   
                return search_result
        
        return False

    def _is_api_key_valid(self,api_key,raise_error=True):
        if not api_key:
            if raise_error:
                raise ValidationError(_("You do not have an API key to connect to Octopart.")) 
            return False
        return True

    def _send_request(self, api_version, api_key, request_body):
        if self._is_api_key_valid(api_key):
            if api_version == 4:
                return self._send_request_V4(api_key,request_body)

        return False

    def _send_request_V4(self, api_key, request_body):
        if not self._is_api_key_valid(api_key):
            return False

        url = 'https://octopart.com/api/v4/endpoint'
        headers = {'Accept': 'application/json',
                'Content-Type': 'application/json'}
        headers['token'] = '{}'.format(api_key)
        req = urllib2.Request(url, json.dumps(request_body).encode('utf-8'), headers)
        try:
            response = urllib2.urlopen(req)
            return response.read().decode('utf-8')
        except urllib2.HTTPError as e:
            logger.error("Octopart query " + str(e.read()))
            raise ValidationError(_("Error on Octopart api requesting.")) 