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
            "extension": file_extension[1:],
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
                        VALUES 
                        (%(name)s, %(extension)s, %(index_content)s, %(full_path)s, %(directory_id)s, %(create_date)s, %(write_date)s, %(month)s, %(year)s, %(write_uid)s, %(create_uid)s, %(user_id)s, %(company_id)s, %(state)s, %(date)s, %(button_save_visible)s)
                    ''' % ({
                "name" : file_attributes["name"],
                "extension" : file_attributes["extension"],
                "index_content" : file_attributes["index_content"],
                "full_path" : file_attributes["full_path"],
                "directory_id" : file_attributes["directory_id"],
                "create_date" : file_attributes["create_date"],
                "write_date" : file_attributes["write_date"],
                "month" : file_attributes["month"],
                "year" : file_attributes["year"],
                "write_uid" : self._uid,
                "create_uid" : self._uid,
                "user_id" : self._uid,
                "company_id" : self.env.user.company_id.id,
                "state" : "draft",
                "date" : file_attributes["date"],
                "button_save_visible" : "False"
            })
        )
        document = self.env["document.openprod"].search([["full_path", "=", file_attributes["full_path"]]], None, 1)
        print(document)
        return document