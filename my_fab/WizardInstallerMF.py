# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class WizardInstallerMF(models.TransientModel):
    _name = 'myfab.installer.mf'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)

    def trigger_wizard(self, cr, uid, context=None):
        print("WIZARD TRIGGERED MF")

    def action_validate_config(self):
        pass
