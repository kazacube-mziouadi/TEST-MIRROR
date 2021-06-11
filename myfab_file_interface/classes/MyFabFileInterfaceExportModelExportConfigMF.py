from openerp import models, fields, api, _


class MyFabFileInterfaceExportModelExportConfigMF(models.Model):
    _inherit = "model.export.config.mf"
    _name = "myfab.file.interface.export.model.export.config.mf"
    _description = "MyFab model export object for a MyFab File Interface Export"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    myfab_file_interface_export_mf = fields.Many2one("myfab.file.interface.export.mf",
                                                     string="MyFab File Interface Export")
