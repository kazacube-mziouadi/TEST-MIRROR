# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class kit_sale(models.TransientModel):
    _inherit = "kit.sale"

    @api.multi
    def create_kit_sale(self):
        #Copy the list of order line ids to know which are added
        memo_sale_id_order_line_ids = []
        for line_id in self.sale_id.order_line_ids:
            memo_sale_id_order_line_ids.append(line_id.id)
        
        res = super(kit_sale, self).create_kit_sale()       

        #Add the new kit to the list
        mf_sale_order_kit_id = self.sale_id.mf_sale_order_line_kit_ids.create({
                            'mf_sale_id' :self.sale_id.id, 
                            'mf_product_id' : self.product_id.id, 
                            'mf_bom_id' : self.bom_id.id,
                            'mf_sec_uom_qty' : self.sec_uom_qty,
                        })

        for line_id in self.sale_id.order_line_ids:
            if line_id.id not in memo_sale_id_order_line_ids:
                line_id.mf_sale_order_kit_id = mf_sale_order_kit_id.id

        return res



        