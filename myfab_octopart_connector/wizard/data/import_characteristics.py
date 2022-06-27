# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class octopart_characteristic_import_wizard(models.TransientModel):
    _name = 'octopart.characteristic.import.wizard'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    explaination = fields.Text(default=(_('Import characteristics of all selected octopart categories')))   
    
    @api.multi
    def import_characteristics(self):
        ids = self.env.context.get('active_ids')
        if self.env['octopart.api.service'].is_api_key_valid():
            for id in ids:
                category_rc = self.env['octopart.category'].search([('id', '=', id)])
                if category_rc:
                    category_rc.get_characteristics()

            return True
        return False