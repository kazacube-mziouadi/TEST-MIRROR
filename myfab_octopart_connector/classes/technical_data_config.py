# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class technical_data_config_settings(models.Model):
    _inherit = 'technical.data.config.settings'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    name = fields.Char()
    octopart_api_key = fields.Char()

    @api.multi
    def write(self, vals):
        res = super(technical_data_config_settings, self).write(vals)

        if 'octopart_api_key' in vals:
            for record in self:
                record.import_all_data()

        return res

    @api.one
    def import_all_data(self):
        if self.env['octopart.api'].check_api_key(False):
            if not self.env['octopart.manufacturer'].search([], None, 1):
                self.env['octopart.manufacturer.import.wizard'].import_manufacturers()
            if not self.env['octopart.seller'].search([], None, 1):
                self.env['octopart.seller.import.wizard'].import_sellers()
            if not self.env['octopart.category'].search([], None, 1):
                self.env['octopart.category.import.wizard'].import_categories()
            #Get all categories to get their characteristics
            category_ids = self.env['octopart.category'].browse()
            if not self.env['characteristic.type'].search([], None, 1) and category_ids:
                self.env['octopart.characteristic.import.wizard'].with_context(category_ids).import_characteristics()