from openerp import models, fields, api, _, modules
import os
import datetime


class DocumentOpenprod(models.Model):
    _inherit = "document.openprod"

    @api.multi
    def unlink(self):
        paths_of_files_to_remove_list = [self.get_file_full_path(document_id) for document_id in self]
        now_formatted = (datetime.datetime.now()).strftime("%Y%m%d%H%M%S%f")
        # Renaming the files to delete to cache files
        for file_path in paths_of_files_to_remove_list:
            os.rename(file_path, self.get_cache_file_name(file_path, now_formatted))
        # Launching default files delete method
        res = super(DocumentOpenprod, self).unlink()
        # Removing the cache files
        for file_path in paths_of_files_to_remove_list:
            os.remove(self.get_cache_file_name(file_path, now_formatted))
        return res

    @staticmethod
    def get_file_full_path(document_id):
        return os.path.join(document_id.directory_id.datadir, document_id.full_path)

    @staticmethod
    def get_cache_file_name(file_path, now_formatted):
        return file_path + "__myfab_cache_" + now_formatted