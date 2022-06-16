# -*- coding: utf-8 -*-

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class technical_data_config_settings(models.Model):
    _inherit = 'technical.data.config.settings'
    
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char()
    octopart_api_key = fields.Char()


    @api.onchange('octopart_api_key')
    def _onchange_load_static_data(self):
        if self.env['octopart.api'].check_api_key():
            self.env['import.manufacturer.wizard'].import_manufacturers()
            self.env['import.seller.wizard'].import_sellers()
            self.env['import.category.wizard'].import_categories()
            #Get all categories to get their characteristics
            category_ids = self.env['octopart.category'].browse()
            if category_ids:
                self.env['import.characteristics.wizard'].with_context(category_ids).import_characteristics()