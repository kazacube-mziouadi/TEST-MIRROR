from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class sale_order(models.Model):
    _inherit = 'sale.order'

    mf_multi_company_purchase_order_id = fields.Many2one('purchase.order', string="Customer purchase order", ondelete='set null')