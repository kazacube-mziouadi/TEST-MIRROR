# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError
from math import *

class stock_move(models.Model):
    _inherit = 'stock.move'

    def generate_labels(self,move_label_to_use_ids = False):
        if len(self.move_label_ids) == 0 or (len(move_label_to_use_ids) > 0 and len(self.move_label_ids) != len(move_label_to_use_ids)):
            create_label_wizard_rc = self.env['create.label.wizard']

            # Wizard initialization
            create_label_wizard_rc.move_id = self.id
            create_label_wizard_rc.product_id = self.product_id.id
            create_label_wizard_rc.uom_id = self.product_id.uom_id.id
            create_label_wizard_rc.sec_uom_id = self.product_id.sec_uom_id.id
            create_label_wizard_rc.label_template_id = self.product_id.label_template_id.id
            create_label_wizard_rc.is_manual_expiry_date = self.product_id.is_expiry_date and self.product_id.expiry_type == 'manual'
            if self.product_id.default_label_qty:
                create_label_wizard_rc.uom_qty = self.product_id.default_label_qty
                create_label_wizard_rc.number_of_label = ceil(self.uom_qty / self.product_id.default_label_qty)
            
            if self.product_id.trigger_box_management:
                create_label_wizard_rc.new_auto_um = self.product_id.trigger_box_management
                create_label_wizard_rc.label_template_um_id = self.product_id.box_type_id.id

            #Wizard completion
            if len(move_label_to_use_ids) > 0:
                create_label_wizard_rc.numer_of_label = len(move_label_to_use_ids)
            else:
                create_label_wizard_rc.numer_of_label = create_label_wizard_rc.move_uom_qty
            create_label_wizard_rc.uom_qty = create_label_wizard_rc.move_uom_qty / create_label_wizard_rc.numer_of_label
            create_label_wizard_rc._onchange_uom_qty()

            create_label_wizard_rc.visualization()
            create_label_wizard_rc.create_label()

            if len(self.move_label_ids) == len(move_label_to_use_ids):
                ind = 0
                for move_label_id in self.move_label_ids:
                    ind += 1
                    move_label_id.mf_label_supplier = move_label_to_use_ids[ind].label_id.name

            self.unprepare()