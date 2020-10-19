from openerp import models, fields, api, _
from IntuizMapInterface import IntuizMapInterface


class ResPartnerTemp(models.TransientModel):
    # Inherits partner
    _name = "res.partner.temp"
    _log_access = True

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    # Adds column score in the partner
    name = fields.Char(string='Name', size=64, required=False, help='')
    mf_score = fields.Integer(string="Score", default=0, required=False)
    street = fields.Char(string='Street', size=64, required=False, help='')
    city = fields.Char(string='City', size=64, required=False, help='')
    zip = fields.Char(string='Zip', size=64, required=False, help='')
    website = fields.Char(string='Website', size=64, required=False, help='')
    siret = fields.Char(string='SIRET', size=64, required=False, help='')

