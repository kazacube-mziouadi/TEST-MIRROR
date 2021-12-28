from openerp import models, fields, api, registry, _


class PhysicalFileMF(models.TransientModel):
    _inherit = "file.mf"
    _name = "physical.file.mf"
    _description = "MyFab physical file"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    directory_path_mf = fields.Char(string="Directory path")

    # ===========================================================================
    # METHODS
    # ===========================================================================
