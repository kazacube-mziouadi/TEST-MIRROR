# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class DocumentDirectory(models.Model):
    # Inherits document.directory
    _inherit = "document.directory"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================

    @api.multi
    def put_documents(self, documents):
        for document in documents:
            if document.directory_id != self:
                document.write({
                    "directory_id": self.id
                })