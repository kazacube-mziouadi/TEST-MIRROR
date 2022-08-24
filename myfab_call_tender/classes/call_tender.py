# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import except_orm, ValidationError

class call_tender(models.Model):
     _inherit = 'call.tender'

     mf_document_ids = fields.Many2many('document.openprod')