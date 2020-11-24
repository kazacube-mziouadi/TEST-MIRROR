from openerp import models, fields, api, _
from CreatableFromObjectTempInterfaceMF import CreatableFromObjectTempInterfaceMF


class ResPartner(models.Model, CreatableFromObjectTempInterfaceMF):
    # Inherits partner
    _inherit = "res.partner"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    # Adds column score in the partner
    score_history_mf = fields.One2many("score.mf", "partner_id_mf", string='History of score')

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @staticmethod
    def create_from_object_temp(self, res_partner_temp, generate_reference=True):
        # As the method is static, "self" is not a ResPartner here, but the "self" of the class using this method.
        object_partner = {
            "name": res_partner_temp.name,
            "score_mf": res_partner_temp.score_mf,
            "street": res_partner_temp.street_mf,
            "city": res_partner_temp.city_mf,
            "zip": res_partner_temp.zip_mf,
            "is_customer": True,
            "siret_number": res_partner_temp.siret_mf
        }
        if generate_reference:
            object_partner["reference"] = self.env['ir.sequence'].get('res.partner')
        return object_partner
