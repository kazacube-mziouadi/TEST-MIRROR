# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class WizardConfirmImportFileMF(models.TransientModel):
    _name = "wizard.confirm.import.file.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    file_interface_import_mf = fields.Many2one("file.interface.import.mf", string="File Interface Import to launch")

    @api.model
    def default_get(self, fields_list):
        res = super(WizardConfirmImportFileMF, self).default_get(fields_list=fields_list)
        res["file_interface_import_mf"] = self.env.context.get("file_interface_import_id")
        return res

    @api.multi
    def action_confirm_import(self):
        self.file_interface_import_mf.launch_button()
