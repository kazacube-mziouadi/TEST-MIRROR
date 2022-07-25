# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    def do_partial(self, lines, make_done=True, transfer_origin_move_rc=False):
        new_picking = super(stock_picking, self).do_partial(lines, make_done=make_done, transfer_origin_move_rc=transfer_origin_move_rc)

        if new_picking:
            new_picking._mf_copy_so_picking_label_to_po_picking()
        
        return new_picking

    def _mf_copy_so_picking_label_to_po_picking(self):
        if self.type == 'out' and self.is_create_label_button:
            po_rc = self.sale_id.mf_get_purchase_order_multi_company()
            if po_rc:
                po_picking_available_rc = po_rc.mf_get_po_picking_available()
                for move_so_rc in self.move_ids:
                    for move_po_rc in po_picking_available_rc.move_ids:
                        if move_so_rc.product_id.track_label and move_so_rc.product_id == move_po_rc.product_id:
                            move_po_rc.generate_labels(move_so_rc.move_label_ids)