from openerp import models, fields, api, _


class FileInterfaceExportModelDictionaryMF(models.Model):
    _inherit = "model.dictionary.mf"
    _name = "file.interface.export.model.dictionary.mf"
    _description = "myfab model dictionary generator for a myfab File Interface Export"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    file_interface_export_mf = fields.Many2one("file.interface.export.mf", required=False, readonly=True,
                                               string="myfab File Interface Export")
    children_model_dictionaries_mf = fields.One2many("file.interface.export.model.dictionary.mf",
                                                     "parent_model_dictionary_mf", ondelete="cascade",
                                                     string="Children model export configs")
