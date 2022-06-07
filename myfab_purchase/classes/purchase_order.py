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
    mf_products_documents_ids = fields.Many2many('document.openprod', 'mf_purchase_product_document_openprod_rel', 'purchase_id', 'document_id', string='Products documents', copy=True)

    @api.onchange('purchase_order_line_ids')
    def _onchange_product_documents(self):
        """
            On récupère tous les documents des produits
        """
        new_docs_ids = []
        new_docs_ids = [document.id for document in self.document_ids]
        # Need to remove first the old products documents added automaticaly before adding the new ones
        new_docs_ids = self._remove_products_documents_automaticaly_added(new_docs_ids)
        new_docs_ids = self._add_products_documents(new_docs_ids)
        # Write method does not work in onchange on many2many fields
        self.document_ids = [(6, 0, new_docs_ids)]

    def _remove_products_documents_automaticaly_added(self, document_ids):
        if document_ids:
            for product_document in self.mf_products_documents_ids:
                document_ids.remove(product_document.id)

        return document_ids

    def _add_products_documents(self,document_ids):
        product_documents_to_add_ids = []
        for product_line in self.purchase_order_line_ids:
            for product_document in product_line.product_id.internal_plan_ids:
                # Check if the product document already is in the list to not over-write those added manualy
                # With this check we add to the automatic list only those which are not already in list
                if not self._document_already_in_list(document_ids,product_document.id):
                    product_documents_to_add_ids.append(product_document.id)
                    document_ids.append(product_document.id)

        # Write method does not work in onchange on many2many fields
        self.mf_products_documents_ids = [(6, 0, product_documents_to_add_ids)]

        return document_ids

    def _document_already_in_list(self,document_ids,current_document_id):
        if current_document_id:
            for purchase_order_document in document_ids:
                if purchase_order_document == current_document_id:
                    return True

        return False