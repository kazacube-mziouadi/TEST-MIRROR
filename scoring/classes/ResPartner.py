from openerp import models, fields, api, _
    
class ResPartner(models.Model, IntuizMapInterface):
    # Inherits partner
    _inherit = "res.partner"

    #===========================================================================
    # COLUMNS
    #===========================================================================
    # Adds column score in the partner
    mf_score = fields.Integer(string="Score", default=0, required=False)

    # ===========================================================================
    # METHODES
    # ===========================================================================
    def map_from_intuiz(self, data):
        self.mf_score = 50.
        self.name = "name from intuiz"
        self.street = "street from intuiz"
        self.city = "city from intuiz"
        self.zip = "zip from intuiz"
        self.website = "website from intuiz"
        self.phone = "phone from intuiz"



