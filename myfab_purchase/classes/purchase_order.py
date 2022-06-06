# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class purchase_order(models.Model):
    """ 
        purchase order
    """
    _inherit = "purchase.order"

    #===========================================================================
    # COLUMNS
    #===========================================================================
    mf_products_documents_ids = fields.Many2many('document.openprod', 'purchase_product_document_openprod_rel', 'purchase_id', 'document_id', string='Products documents', copy=True)

    @api.onchange('purchase_order_line_ids')
    def _onchange_product_documents(self):
        """
            On récupère tous les documents des produits
        """
        product_docs_to_add_ids = []
        new_docs_ids = []

        # Copy all ids of documents
        new_docs_ids = [document.id for document in self.document_ids]

        # Remove from the documents those from product document
        for product_document in self.mf_products_documents_ids:
            new_docs_ids.remove(product_document.id)

        # Add the document from product if they are not already in the list
        for product_line in self.purchase_order_line_ids:
            for product_document in product_line.product_id.internal_plan_ids:
                document_already_exists = False
                for purchase_order_document in new_docs_ids:
                    if purchase_order_document == product_document.id:
                        document_already_exists = True

                if not document_already_exists:
                    product_docs_to_add_ids.append(product_document.id)
                    new_docs_ids.append(product_document.id)
    
        # Update both lists of documents
        self.document_ids = [(6, 0, new_docs_ids)]
        self.mf_products_documents_ids = [(6, 0, product_docs_to_add_ids)]