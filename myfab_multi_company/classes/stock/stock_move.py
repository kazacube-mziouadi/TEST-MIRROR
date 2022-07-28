# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError
from math import *

class stock_move(models.Model):
    _inherit = 'stock.move'

    def mf_generate_labels(self,move_label_to_use_ids = False):      
        if len(self.move_label_ids) == 0 or (len(move_label_to_use_ids) > 0 and len(self.move_label_ids) != len(move_label_to_use_ids)):
            create_label_wizard_id = self._mf_create_label_wizard_qty(len(move_label_to_use_ids))
            #Sudo needed to write elements on the other company
            create_label_wizard_id.sudo().create_label()
            if len(move_label_to_use_ids) > 0 and len(self.move_label_ids) == len(move_label_to_use_ids):
                ind = 0
                for move_label_id in self.move_label_ids:
                    move_label_id.label_id.mf_label_supplier = move_label_to_use_ids[ind].label_id.name
                    ind += 1

    def _mf_create_label_wizard_init(self, create_label_wizard_id = False):
        vals = {
            'move_id': self.id,
            'product_id': self.product_id.id,
            'uom_id': self.product_id.uom_id.id,
            'sec_uom_id': self.product_id.sec_uom_id.id,
            'label_template_id': self.product_id.label_template_id.id,
            'is_manual_expiry_date': self.product_id.is_expiry_date and self.product_id.expiry_type == 'manual',
            'uom_qty':self.product_id.default_label_qty,
        }

        if not create_label_wizard_id:
            #Sudo needed to write elements on the other company
            create_label_wizard_id = self.env['create.label.wizard'].sudo().create(vals)
 
        if self.product_id.default_label_qty:
            vals['number_of_label'] = ceil(self.uom_qty / self.product_id.default_label_qty)
        
        if self.product_id.trigger_box_management:
            vals['new_auto_um'] = self.product_id.trigger_box_management
            vals['label_template_um_id'] = self.product_id.box_type_id.id

        create_label_wizard_id.write(vals)

        return create_label_wizard_id

    def _mf_create_label_wizard_qty(self,number_of_label,create_label_wizard_id = False):        
        if not create_label_wizard_id:
            create_label_wizard_id = self._mf_create_label_wizard_init()

        final_number_of_label = number_of_label if number_of_label > 0 else create_label_wizard_id.move_uom_qty

        vals = {
            'number_of_label': final_number_of_label,
            'uom_qty': create_label_wizard_id.move_uom_qty / final_number_of_label,
        }

        create_label_wizard_id.write(vals)
        create_label_wizard_id._onchange_uom_qty()

        #Sudo needed to write elements on the other company
        create_label_wizard_id.sudo().visualization()

        return create_label_wizard_id