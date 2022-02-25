# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class WizardNoImportFileMF(models.TransientModel):
    _name = "wizard.no.import.file.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
