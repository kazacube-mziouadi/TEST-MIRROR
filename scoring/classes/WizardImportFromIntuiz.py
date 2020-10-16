from openerp import models, fields, api, _

from IntuizApi import IntuizApi
from IntuizApiSearch import IntuizApiSearch

import xml.etree.ElementTree as ET

class WizardImportFromIntuiz(models.TransientModel):
    _name = 'wizard.partner.import.intuiz'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string='Name', size=32, required=False)

    @api.multi
    def action_validate(self):
        intuiz_api = IntuizApi()
        intuiz_api_search = IntuizApiSearch(intuiz_api, "", "")
        response = intuiz_api_search.send()
        responseParsed = ET.fromstring(response)
        partners_to_choose = [responseParsed[0][0][0][3]]
        for partner in partners_to_choose:
            print(partner)
