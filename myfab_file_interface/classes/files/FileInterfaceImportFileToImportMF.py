from openerp import models, fields, api, registry, _


class FileInterfaceImportFileToImportMF(models.TransientModel):
    _inherit = "physical.file.mf"
    _name = "file.interface.import.file.to.import.mf"
    _description = "MyFab File Interface Import physical file to import"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    file_interface_import_mf = fields.Many2one("file.interface.import.mf", string="MyFab file interface import")
