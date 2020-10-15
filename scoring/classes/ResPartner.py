from openerp import models, fields, api, _
    
class ResPartner(models.Model):
    # Inherits partner
    _inherit = "res.partner"

    #===========================================================================
    # COLUMNS
    #===========================================================================
    # Adds column score in the partner
    mf_score = fields.Integer(string="Score", default=0, required=False)
