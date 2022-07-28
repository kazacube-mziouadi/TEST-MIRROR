# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class stock_move_label(models.Model):
    _inherit = 'stock.move.label'

    mf_label_supplier = fields.Char(string = "Label supplier", readonly=True, related="label_id.mf_label_supplier")