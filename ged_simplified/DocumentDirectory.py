# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class DocumentDirectory(models.Model):
    # Inherits document.directory
    _inherit = "document.directory"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================


    def put_documents(self, documents):
        print("####DocumentDirectory::put_document - in")
        for document in documents:
            print("########DocumentDirectory::put_document - for : " + document.name)
            if document.directory_id != self:
                print("############DocumentDirectory::put_document - for : " + document.name + " write.")
                document.write({
                    "directory_id": self.id
                })
            else:
                print("############DocumentDirectory::put_document - for : " + document.name + " not write.")