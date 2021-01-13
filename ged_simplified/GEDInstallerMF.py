# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class GEDInstallerMF(models.TransientModel):
    _name = 'ged.installer.mf'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)

    @api.model
    def trigger_installer(self):
        root_directory = self.env["document.directory"].search([], None, 1)
        partners_directory = self.env["document.directory"].search([["name", "=", "Partners"]], None, 1)
        if not partners_directory:
            self.env["document.directory"].create({
                "name": "Partners",
                "model_directory": True,
                "root_directory": False,
                "parent_id": root_directory.id,
                "active": True
            })
        partners = self.env["res.partner"].search([])

        for partner in partners:
            partner.create_directory()
            partner.put_documents_in_current_directory()




