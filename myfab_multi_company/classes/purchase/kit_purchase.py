# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class kit_purchase(models.TransientModel):
    _inherit = "kit.purchase"

    @api.multi
    def create_kit_purchase(self):
        #Copy the list of order line ids to know which are added
        memo_purchase_order_line_ids = []
        for line_id in self.purchase_id.purchase_order_line_ids:
            memo_purchase_order_line_ids.append(line_id.id)
        
        res = super(kit_purchase, self).create_kit_purchase()   

        new_purchase_order_line_ids = []
        for line_id in self.purchase_id.purchase_order_line_ids:
            if line_id.id not in memo_purchase_order_line_ids:
                new_purchase_order_line_ids.append((0,0,{'id' : line_id.id}))      

        #Add the new kit to the list
        self.purchase_id.mf_purchase_order_line_kit_ids = [(0,0,{
                            'mf_purchase_id' :self.purchase_id.id, 
                            'mf_product_id' : self.product_id.id, 
                            'mf_bom_id' : self.bom_id.id,
                            'mf_sec_uom_qty' : self.sec_uom_qty,
                            'mf_purchase_order_line_ids' : new_purchase_order_line_ids,
                        })]

        return res