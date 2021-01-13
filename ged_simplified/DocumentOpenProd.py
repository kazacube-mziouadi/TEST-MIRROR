# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from os import walk, path
import time
from datetime import datetime

class DocumentOpenProd(models.Model):
    # Inherits document.directory
    _inherit = "document.openprod"

    def compute_link_document(self, document_path):
        created_timestamp = time.ctime(os.path.getctime(document_path))
        last_modified_timestamp = time.ctime(os.path.getmtime(document_path))
        month_number = datetime.fromtimestamp(last_modified_timestamp).strftime('%m')
        year_number = datetime.fromtimestamp(last_modified_timestamp).strftime('%Y')
        print("last modified: %s" % time.ctime(os.path.getmtime(document_path)))
        print("created: %s" % time.ctime(os.path.getctime(document_path)))
        print(document_path)
        with open(document_path, 'r') as f:
            file_content = f.read()
        filename_split = filename.split('.')
        file_attributes = {
            "name": filename_split[0],
            "extension": filename_split[1],
            "index_content": file_content,
            "full_path": document_path,
            "directory_id": self.directory_id_mf.id,
            "create_date": created_timestamp,
            "write_date": last_modified_timestamp,
            "month": month_number,
            "year": year_number
        }
        self.env.cr.execute('''
                        INSERT INTO
                            document_openprod
                        (name, extension, index_content, full_path, directory_id, create_date, write_date, month, year, write_uid, create_uid, user_id, company_id, state)
                        VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
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
                self.env.company.id,
                "draft"
            )
        )