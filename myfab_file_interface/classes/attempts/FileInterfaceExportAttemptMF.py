from openerp import models, fields, api, registry, _


class FileInterfaceExportAttemptMF(models.Model):
    _inherit = "file.interface.attempt.mf"
    _name = "file.interface.export.attempt.mf"
    _description = "myfab file interface export attempt"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    file_interface_export_mf = fields.Many2one("file.interface.export.mf", required=False,
                                               string="myfab file interface export")
