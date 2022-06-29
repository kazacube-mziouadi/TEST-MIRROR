# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    mf_purchase_order_line_kit_ids = fields.One2many('mf.purchase.order.line.kit', 'mf_purchase_id',  string='Purchase order line kit', copy=False)

    @api.onchange('mf_purchase_order_line_kit_ids')
    def _onchange_refresh_dependancies(self):
        self.purchase_order_line_ids.refresh()
        self._onchange_purchase_order_line_ids()

    @api.multi
    def action_progress_purchase_state(self):
        res = super(purchase_order, self).action_progress_purchase_state()

        if self.multi_company_sale_order_id:
            mf_sale_order_line_kit_ids = []
            for kit_id in self.mf_purchase_order_line_kit_ids:
                mf_sale_order_line_kit_ids.create((0,0,{
                    'mf_sale_id':self.multi_company_sale_order_id.id,
                    'mf_product_id':kit_id.mf_product_id.id,
                    'mf_bom_id':kit_id.mf_bom_id.id,
                    'mf_sec_uom_qty':kit_id.mf_sec_uom_qty,
                }))

        return res
