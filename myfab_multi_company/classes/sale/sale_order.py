from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class sale_order(models.Model):
    _inherit = 'sale.order'

    mf_multi_company_purchase_order_id = fields.Many2one('purchase.order', string="Customer purchase order", ondelete='set null')
    mf_multi_company_purchase_order_name = fields.Char(string="Customer purchase order", compute="_mf_compute_get_name")

    @api.one
    def _mf_compute_get_name(self):
        self.mf_multi_company_purchase_order_name = self.mf_get_purchase_order_multi_company().name

    def mf_get_purchase_order_multi_company(self):
        customer_company_rc = self.env['res.company'].sudo().search([('partner_id', '=', self.partner_id.id)])
        customer_user_rc = customer_company_rc.default_company_user_id

        return self.mf_multi_company_purchase_order_id.sudo(customer_user_rc).with_context(active_company_id=customer_company_rc.id)
