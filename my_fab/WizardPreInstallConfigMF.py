from openerp import models, fields, api, _

class WizardPreInstallConfigMF(models.TransientModel):
    _name = "wizard.myfab.preinstall.config.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)




