from openerp import models, fields, api, registry, _


class FileInterfaceImportMF(models.Model):
    _inherit = "file.interface.import.mf"

    # ===========================================================================
    # METHODS - COLUMNS
    # ===========================================================================
    file_extension_mf = fields.Selection(selection_add=[("csv_manitou", "CSV Manitou")])

    @api.one
    def import_file(self, file_content, file_name):
        super(FileInterfaceImportMF, self).import_file(file_content, file_name)
        if self.file_extension_mf == "csv_manitou":
            self.env["mf.called.sale.order.generator.service"].generate_called_sales_order()
