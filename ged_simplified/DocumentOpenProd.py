# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import time
import os
from datetime import datetime

class DocumentOpenProd(models.Model):
    # Inherits document.directory
    _inherit = "document.openprod"

    def compute_link_document(self, document_path, directory):
        print("DocumentOpenProd::compute_link_document")
        print(self)
        print(document_path)
        print(directory)
        created_timestamp = time.ctime(os.path.getctime(document_path))
        last_modified_timestamp = time.ctime(os.path.getmtime(document_path))
        last_modified_date = datetime.fromtimestamp(os.path.getmtime(document_path))
        print(document_path)
        filename = os.path.basename(document_path)
        with open(document_path, 'r') as f:
            file_content = f.read()
        file_base_name, file_extension = os.path.splitext(filename)
        file_attributes = {
            "name": file_base_name,
            "extension": file_extension,
            "index_content": file_content,
            "full_path": os.path.join(directory.full_path, filename),
            "directory_id": directory.id,
            "create_date": created_timestamp,
            "write_date": last_modified_timestamp,
            "month": last_modified_date.strftime('%m'),
            "year": last_modified_date.strftime('%Y'),
            "date": last_modified_date.strftime('%Y-%m-%d')
        }
        self.env.cr.execute('''
                        INSERT INTO
                            document_openprod
                        (name, extension, index_content, full_path, directory_id, create_date, write_date, month, year, write_uid, create_uid, user_id, company_id, state, date, button_save_visible)
                        VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', %s)
                    ''' % (
                file_attributes["name"],
                file_attributes["extension"],
                file_attributes["index_content"],
                file_attributes["full_path"],
                file_attributes["directory_id"],
                file_attributes["create_date"],
                file_attributes["write_date"],
                file_attributes["month"],
                file_attributes["year"],
                self._uid,
                self._uid,
                self._uid,
                self.env.user.company_id.id,
                "draft",
                file_attributes["date"],
                "False")
        )
        document = self.env["document.openprod"].search([["full_path", "=", file_attributes["full_path"]]], None, 1)
        print(document)
        return document