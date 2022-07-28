# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_progress_purchase_state(self):
        res = super(purchase_order, self).action_progress_purchase_state()

        if self.multi_company_sale_order_id:
            so_id = self.mf_get_sale_order_multi_company()
            if self.is_automatic_sale:
                so_id.mf_multi_company_purchase_order_id = self.id
            else:
                so_id.mf_multi_company_purchase_order_id = False

        return res

    def mf_get_sale_order_multi_company(self):
        seller_company_rc = self.env['res.company'].sudo().search([('partner_id', '=', self.partner_id.id)])
        seller_user_rc = seller_company_rc.default_company_user_id
        
        return self.multi_company_sale_order_id.sudo(seller_user_rc).with_context(active_company_id=seller_company_rc.id)

    def mf_get_po_picking_available(self):
        picking_available_rc = False

        for picking_rc in self.picking_ids:
            if picking_available_rc == False and picking_rc.type == 'in' and picking_rc.state == 'waiting':
                picking_available_rc = picking_rc

        if not picking_available_rc:
            self.action_generate_picking()
            picking_available_rc = self.mf_get_po_picking_available()

        return picking_available_rc
