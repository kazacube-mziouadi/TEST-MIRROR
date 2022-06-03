# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class purchase_order(models.Model):
    """ 
        purchase order
    """
    _inherit = "purchase.order"

    @api.one   
    @api.depends('purchase_order_line_ids')
    def _compute_product_documents(self):
        """
            On récupère tous les documents des produits
        """
        for line in self.purchase_order_line_ids:
            for product_document_id in line.product_id.internal_plan_ids:
                document_already_exists = False
                for document_id in self.document_ids:
                    if document_id.id == product_document_id.id:
                        document_already_exists = True
                if not document_already_exists:	
                    self.document_ids.append(product_document_id)