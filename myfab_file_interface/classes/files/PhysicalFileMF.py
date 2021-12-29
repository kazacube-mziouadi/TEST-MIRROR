from openerp import models, fields, api, registry, _
import os


class PhysicalFileMF(models.TransientModel):
    _inherit = "file.mf"
    _name = "physical.file.mf"
    _description = "MyFab physical file"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    directory_path_mf = fields.Char(string="Directory path")
    last_modification_date_mf = fields.Datetime(string="Last modification date")

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.multi
    def delete(self):
        file_path = os.path.join(self.directory_path_mf, self.name)
        if os.path.exists(file_path):
            os.remove(file_path)
            self.unlink()
            # Reload view to update files list
            return {'type': 'ir.actions.act_window_view_reload'}
