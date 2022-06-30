from openerp import models, fields, api, registry, _


class RecordImportRowMF(models.Model):
    _name = "record.import.row.mf"
    _description = "myfab import record's row"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, help='')
    record_import_mf = fields.Many2one("file.interface.import.attempt.record.import.mf", string="Record import",
                                       ondelete="cascade")
    row_number_mf = fields.Integer(string="Row number")
    row_content_mf = fields.Char(string="Row content")
