# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

class xml_preprocessing_table_rule(models.Model):
    _inherit = "xml.preprocessing.table.rule"

    #===========================================================================
    # COLUMN
    #===========================================================================
    #Modification parameter
    mf_modif_old_value = fields.Char(string="Old value")