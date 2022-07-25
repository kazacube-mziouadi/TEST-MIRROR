# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class stock_move_line(models.Model):
    _inherit = 'stock.move.label'

    mf_label_supplier = fields.Char()