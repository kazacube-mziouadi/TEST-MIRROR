# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase
from openerp.tools.translate import _

class test_scoring(TransactionCase):
    """
        Tests d'import et mise a jour des donnees de client via Intuiz.
    """

    def setUp(self):
        super(test_scoring, self).setUp()
        self.partner_model = self.env["res.partner"].create({
            "name": "TEST_PARTNER",
            "zip": "38",
            "country": "Afghanistan",
            "is_customer": True,
            "siret_number": "35197753300022",
            "reference": self.env['ir.sequence'].get('res.partner')
        })

    def test_update_partner_data(self):
        intuiz_api_identity = self.env["intuiz.api.identity.mf"].create({})
        res_partner_temps = intuiz_api_identity.get_partners_temp(self.partner_model.zip,
                                                                  self.partner_model.siret_number)
        res_partner_temp = self.env["res.partner.temp.mf"].search([["id", "=", res_partner_temps[0]]], None, 1)
        self.partner_model.write(self.env["res.partner"].create_from_object_temp(self, res_partner_temp, False))
        self.assertEquals(self.partner_model.zip, "38850", _("The ZIP isn't right"))