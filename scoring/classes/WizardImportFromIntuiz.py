from openerp import models, fields, api, _
from IntuizApiService import IntuizApiService
import xml.etree.ElementTree as ET


class WizardImportFromIntuiz(models.TransientModel):
    _name = 'wizard.partner.import.intuiz'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string='Name', size=32, required=False)

    @api.multi
    def action_validate(self):
        intuiz_api_service = IntuizApiService("", "")
        partners_to_choose = intuiz_api_service.getPartners()
