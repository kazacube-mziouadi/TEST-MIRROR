from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class sale_order(models.Model):
    _inherit = 'sale.order'

    mf_multi_company_purchase_order_id = fields.Many2one('purchase.order', string="Customer purchase order", ondelete='set null')

    def mf_get_purchase_order_multi_company(self):
        company_rc = self.env['res.company'].sudo().search([('partner_id', '=', self.partner_id.id)])
        user_rc = company_rc.default_company_user_id
        return self.mf_multi_company_purchase_order_id.sudo(user_rc).with_context(active_company_id=company_rc.id)
