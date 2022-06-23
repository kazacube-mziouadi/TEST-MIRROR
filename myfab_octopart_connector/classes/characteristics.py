# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class characteristic(models.Model):
    _inherit = 'characteristic'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    octopart_unit = fields.Char()
    octopart_result_id = fields.Many2one('octopart.research.result', string='Result search', required=False, ondelete='cascade')
    
class characteristic_type(models.Model):
    _inherit = 'characteristic.type'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    octopart_category_ids = fields.Many2many('octopart.category', string='Octopart category')
    octopart_unit = fields.Char()
    octopart_key = fields.Char()
    
class characteristic_value(models.Model):
    _inherit = 'characteristic.value'
    
    #===========================================================================
    # COLUMNS
    #===========================================================================
    octopart_category_ids = fields.Many2many('octopart.category', string='Octopart category')