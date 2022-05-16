from openerp import models, fields, api, _, modules
import os


class DocumentOpenprod(models.Model):
    _inherit = "document.openprod"

    @api.multi
    def unlink(self):
        paths_of_files_to_remove_list = [self.get_file_full_path(document_id) for document_id in self]
        res = super(DocumentOpenprod, self).unlink()
        for file_path in paths_of_files_to_remove_list:
            print(file_path)
            print(os.path.exists(file_path))
            if os.path.exists(file_path):
                os.system("rm " + file_path)
            print(os.path.exists(file_path))
        return res

    @staticmethod
    def get_file_full_path(document_id):
        return os.path.join(document_id.directory_id.datadir, document_id.full_path)