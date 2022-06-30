from openerp import models, fields, api, _, modules
import datetime


class Intervention(models.Model):
    _inherit = "intervention"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    x_mf_signature = fields.Binary(string="Signature")
    x_mf_signature_contact_id = fields.Many2one("res.partner", string="Signing contact")
    x_mf_signature_datetime = fields.Datetime(string="Signature datetime", compute="_compute_mf_signature_date",
                                              readonly=True, store=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.one
    @api.depends("x_mf_signature")
    def _compute_mf_signature_date(self):
        if self.x_mf_signature:
            self.x_mf_signature_datetime = datetime.datetime.now()

    @api.one
    @api.onchange("contact_id")
    def _onchange_mf_signature_contact_id(self):
        if not self.x_mf_signature_contact_id:
            self.x_mf_signature_contact_id = self.contact_id
