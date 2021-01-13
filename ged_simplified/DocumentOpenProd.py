# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class DocumentOpenProd(models.Model):
    # Inherits document.directory
    _inherit = "document.openprod"

    def compute_link_document(self, document_tmp):
        self.env.cr.execute('''
                        INSERT INTO
                            document_openprod
                        (name, extension, index_content, full_path, directory_id)
                        VALUES ('%s','%s','%s','%s','%s')
                    ''' % (
                document_tmp["name"],
                document_tmp["extension"],
                document_tmp["index_content"],
                document_tmp["full_path"],
                document_tmp["directory_id"]
            )
        )