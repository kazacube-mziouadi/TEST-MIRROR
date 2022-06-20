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

class octopart_characteristic_import_wizard(models.TransientModel):
    _name = 'octopart.characteristic.import.wizard'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    explaination = fields.Text(default=(_('Import characteristics of all select octopart category')))   
    
    @api.multi
    def import_characteristics(self):
        ids = self.env.context.get('active_ids')
        if self.env['octopart.api'].check_api_key():
            for id in ids:
                category_rc = self.env['octopart.category'].search([('id', '=', id)])
                category_rc.get_characteristics()

            return True
        return False