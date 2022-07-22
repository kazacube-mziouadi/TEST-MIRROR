# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_progress_purchase_state(self):
        res = super(purchase_order, self).action_progress_purchase_state()

        if self.multi_company_sale_order_id:
            company_rc = self.env['res.company'].sudo().search([('partner_id', '=', self.partner_id.id)])
            user_rc = company_rc.default_company_user_id
            so_id = self.multi_company_sale_order_id.sudo(user_rc).with_context(active_company_id=company_rc.id)
            if self.is_automatic_sale:
                so_id.mf_multi_company_purchase_order_id = self.id
            else:
                so_id.mf_multi_company_purchase_order_id = False

        return res
