# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError
import openerp.addons.decimal_precision as dp

class mf_purchase_order_line_kit(models.Model):
    _name = "mf.purchase.order.line.kit"
    _description = "Purchase order line kit"

    mf_purchase_id = fields.Many2one('purchase.order', string='purchase', readonly=True, ondelete='cascade')
    mf_product_id = fields.Many2one('product.product', string='Product', readonly=True, ondelete='cascade', 
                                 domain=[('type', '=', 'service'), ('purchase_ok', '=', True), ('manage_service_receipt', '=', True)])
    mf_bom_id = fields.Many2one('mrp.bom', string='Bom', readonly=True, ondelete='cascade')
    mf_sec_uom_qty = fields.Float(string='Quantity in purchase unity', default=0.0, digits=dp.get_precision('Product quantity'), 
                               readonly=True)
    mf_purchase_order_line_ids = fields.One2many('purchase.order.line', 'mf_purchase_order_kit_id',  string='Purchase order kit', copy=False)