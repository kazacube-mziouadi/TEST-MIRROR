from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, CancelError

class sale_order(models.Model):
    _inherit = 'sale.order'

    mf_sale_order_line_kit_ids = fields.One2many('mf.sale.order.line.kit', 'mf_sale_id',  string='sale order line kit', copy=False)