# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError
import openerp.addons.decimal_precision as dp

class mf_sale_order_line_kit(models.Model):
    _name = "mf.sale.order.line.kit"
    _description = "sale order line kit"

    mf_sale_id = fields.Many2one('sale.order', string='Sale', readonly=True, ondelete='cascade')
    mf_product_id = fields.Many2one('product.product', string='Product', readonly=True, ondelete='cascade', 
                                 domain=[('type', '=', 'service'), ('sale_ok', '=', True),('manage_service_delivery', '=', True)])
    mf_bom_id = fields.Many2one('mrp.bom', string='Bom', readonly=True, ondelete='cascade')
    mf_sec_uom_qty = fields.Float(string='Quantity in sale unity', default=0.0, digits=dp.get_precision('Product quantity'), 
                               readonly=True)
    mf_sale_order_line_ids = fields.One2many('sale.order.line', 'mf_sale_order_kit_id',  string='sale order kit', copy=False)