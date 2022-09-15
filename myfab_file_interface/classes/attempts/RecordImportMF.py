from openerp import models, fields, api, registry, _


class RecordImportMF(models.AbstractModel):
    _name = "record.import.mf"
    _description = "myfab import's record"
    _auto = False

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def _links_get(self):
        model_pool = self.env["ir.model"]
        res = model_pool.search([]).read(["model", "name"])
        return [(r["model"], r["name"]) for r in res] + [('', '')]

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, help='')
    method_mf = fields.Char(string="Method applied")
    model_mf = fields.Many2one("ir.model", string="Model")
    fields_mf = fields.Text(string="Record's fields")
    fields_to_write_mf = fields.Text(string="Record's fields to write")
    status_mf = fields.Selection(
        [("not processed", _("Not processed")), ("success", _("Success")), ("failed", _("Failed")), ("ignored", _("Ignored"))],
        "Status", default="not processed", readonly=True
    )
    committed_mf = fields.Boolean(string="Committed", default=False)
    callback_method_mf = fields.Char(string="Method called on record", help="")
    mf_linked_record_reference = fields.Reference(string="Linked record's reference", selection=_links_get, size=128)
