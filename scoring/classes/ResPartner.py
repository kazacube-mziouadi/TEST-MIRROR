from openerp import models, fields, api, _
from IntuizMapInterface import IntuizMapInterface
from IntuizApiService import IntuizApiService

class ResPartner(models.Model, IntuizMapInterface):
    # Inherits partner
    _inherit = "res.partner"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    # Adds column score in the partner
    mf_score = fields.Integer(string="Score", default=0, required=False)
    name = fields.Char(string='Name', size=64, required=False, help='')
    street = fields.Char(string='Street', size=64, required=False, help='')
    city = fields.Char(string='City', size=64, required=False, help='')
    zip = fields.Char(string='Zip', size=64, required=False, help='')
    website = fields.Char(string='Website', size=64, required=False, help='')
    phone = fields.Char(string='Phone', size=64, required=False, help='')

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def map_from_intuiz(self, data):
        self.mf_score = 50.
        self.name = "name from intuiz"
        self.street = "street from intuiz"
        self.city = "city from intuiz"
        self.zip = "zip from intuiz"
        self.website = "website from intuiz"
        self.phone = "phone from intuiz"
