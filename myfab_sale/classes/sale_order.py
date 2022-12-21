# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sale_order(models.Model):
    """ 
        sale order
    """
    _inherit = "sale.order"

    def _mf_recompute_sale_info(self):
        self.onchange_sale_order_line_ids(False)
        wizard = self.env['change.account.system'].create({
            'sale_id':self.id,  
            'sale_account_system_id':self.env['account.fiscal.position'].search([("name","=",self.delivered_country_id.name)]).id
        })
        wizard.change_account_system()

