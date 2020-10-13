from openerp import models, fields, api, _
    
class res_partner(models.Model):
    # Inherits partner and adds instructor information in the partner form
    _inherit = 'res.partner'

    #===========================================================================
    # COLUMNS
    #===========================================================================
    mf_score = fields.Integer(string='Score', default=0, required=False)



