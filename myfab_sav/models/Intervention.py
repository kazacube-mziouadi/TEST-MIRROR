from openerp import models, fields, api, _, modules
import datetime


class Intervention(models.Model):
    _inherit = "intervention"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    client_signature = fields.Binary(string="Client signature")
    mf_signature_contact_id = fields.Many2one("res.partner", string="Signing contact")
    mf_signature_date = fields.Datetime(string="Signature date", compute="_compute_mf_signature_date", readonly=True,
                                        store=True)
    mf_is_signature_contact_id_readonly = fields.Boolean(default=False, readonly=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.multi
    def write(self, vals):
        if "client_signature" in vals:
            vals["mf_is_signature_contact_id_readonly"] = True
        return super(Intervention, self).write(vals)

    @api.one
    @api.depends("client_signature")
    def _compute_mf_signature_date(self):
        if self.client_signature:
            self.mf_signature_date = datetime.datetime.now()

    @api.one
    @api.onchange("client_signature", "contact_id")
    def _onchange_mf_signature_contact_id(self):
        if not self.mf_signature_contact_id:
            self.mf_signature_contact_id = self.contact_id
        if not self.client_signature:
            self.mf_is_signature_contact_id_readonly = False

