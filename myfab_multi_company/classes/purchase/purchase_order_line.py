# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    mf_purchase_order_kit_id = fields.Many2one('mf.purchase.order.line.kit', string='Purchase order line kit', ondelete='cascade')