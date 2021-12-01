from openerp import models, fields, api, registry, _


class FileInterfaceImportAttemptMF(models.Model):
    _inherit = "file.interface.attempt.mf"
    _name = "file.interface.import.attempt.mf"
    _description = "MyFab file interface import attempt"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    file_interface_import_mf = fields.Many2one("file.interface.import.mf", required=False,
                                               string="MyFab file interface import")
