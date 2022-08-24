# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class stock_label(models.Model):
    _inherit = 'stock.label'

    mf_label_supplier = fields.Char(string = "Supplier label", readonly=True, default=False)