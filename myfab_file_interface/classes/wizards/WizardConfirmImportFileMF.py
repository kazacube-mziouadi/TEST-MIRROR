# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class WizardConfirmImportFileMF(models.TransientModel):
    _name = "wizard.confirm.import.file.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    file_interface_import_mf = fields.Many2one("file.interface.import.mf", string="File Interface Import to launch")

    @api.multi
    def action_confirm_import(self):
        self.file_interface_import_mf.import_files()
