# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    mf_sale_order_kit_id = fields.Many2one('mf.sale.order.line.kit', string='Kit', readonly=True, ondelete='cascade')