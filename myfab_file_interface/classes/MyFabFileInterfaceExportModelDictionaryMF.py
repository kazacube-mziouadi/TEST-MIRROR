from openerp import models, fields, api, _


class MyFabFileInterfaceExportModelDictionaryMF(models.Model):
    _inherit = "model.dictionary.mf"
    _name = "myfab.file.interface.export.model.dictionary.mf"
    _description = "MyFab model dictionary generator for a MyFab File Interface Export"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    myfab_file_interface_export_mf = fields.Many2one("myfab.file.interface.export.mf", required=False, readonly=True,
                                                     string="MyFab File Interface Export")
    children_model_dictionaries_mf = fields.One2many("myfab.file.interface.export.model.dictionary.mf",
                                                     "parent_model_dictionary_mf", ondelete="cascade",
                                                     string="Children Model Export Configs")
