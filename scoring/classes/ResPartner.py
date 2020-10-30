from openerp import models, fields, api, _
from IntuizMapInterfaceMF import IntuizMapInterfaceMF


class ResPartner(models.Model, IntuizMapInterfaceMF):
    # Inherits partner
    _inherit = "res.partner"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    # Adds column score in the partner
    score_mf = fields.Integer(string="Score", default=0, required=False)
    score_history_mf = fields.One2many("score.mf", "partner_id_mf", copy=False)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def map_from_intuiz(self, data):
        self.score_mf = 50.
        self.name = "name from intuiz"
        self.street = "street from intuiz"
        self.city = "city from intuiz"
        self.zip = "zip from intuiz"
        self.website = "website from intuiz"
        self.phone = "phone from intuiz"