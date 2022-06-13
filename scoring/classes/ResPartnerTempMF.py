from openerp import models, fields, api, _
from CreatableFromObjectTempInterfaceMF import CreatableFromObjectTempInterfaceMF


class ResPartnerTempMF(models.TransientModel, CreatableFromObjectTempInterfaceMF):
    # Inherits partner
    _name = "res.partner.temp.mf"
    _log_access = True

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string='Name', size=64, required=False, help='')
    score_mf = fields.Integer(string="Score", default=0, required=False)
    street_mf = fields.Char(string='Street', size=64, required=False, help='')
    city_mf = fields.Char(string='City', size=64, required=False, help='')
    zip_mf = fields.Char(string='Zip', size=64, required=False, help='')
    website_mf = fields.Char(string='Website', size=64, required=False, help='')
    siret_mf = fields.Char(string='SIRET', size=64, required=False, help='')
    selected_mf = fields.Boolean(string='Selected', default=False)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @staticmethod
    def create_from_object_temp(partner_temp_api):
        return {
            "name": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}raisonSociale").text,
            "street_mf": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}rue").text,
            "city_mf": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}ville").text,
            "zip_mf": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}codePostal").text,
            "siret_mf": partner_temp_api.find("{http://vo.callisto.newsys.altares.fr/xsd}siret").text
        }
