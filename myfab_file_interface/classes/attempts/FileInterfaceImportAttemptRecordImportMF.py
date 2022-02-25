from openerp import models, fields, api, registry, _


class FileInterfaceImportAttemptRecordImportMF(models.Model):
    _inherit = "record.import.mf"
    _name = "file.interface.import.attempt.record.import.mf"
    _description = "MyFab file interface import attempt's record import object"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    file_interface_import_attempt_mf = fields.Many2one("file.interface.import.attempt.mf", required=False,
                                                       string="MyFab file interface import attempt")
