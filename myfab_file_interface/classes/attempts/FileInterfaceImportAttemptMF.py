from openerp import models, fields, api, registry, _
import base64


class FileInterfaceImportAttemptMF(models.Model):
    _inherit = "file.interface.attempt.mf"
    _name = "file.interface.import.attempt.mf"
    _description = "MyFab file interface import attempt"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    file_interface_import_mf = fields.Many2one("file.interface.import.mf", required=False,
                                               string="MyFab file interface import")

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.multi
    def import_file_again(self):
        importer_service = self.env["importer.service.mf"].create({})
        self.file_interface_import_mf.import_file(
            importer_service, base64.b64decode(self.file_content_mf), self.file_name_mf
        )
