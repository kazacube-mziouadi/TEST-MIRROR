from openerp import models, fields


class Intervention(models.Model):
    _inherit = "intervention"

    client_signature = fields.Binary(string="Client signature")
