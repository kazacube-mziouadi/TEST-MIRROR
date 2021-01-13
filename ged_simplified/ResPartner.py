# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class ResPartner(models.Model):
    # Inherits document.openprod
    _inherit = "res.partner"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    _directory_id_mf = fields.Many2one("document.directory", string="Directory")

    @property
    def directory_id_mf(self):
        if self._directory_id_mf:
            return self._directory_id_mf
        partner_directory_name = self.name
        partners_directory = self.env["document.directory"].search([["name", "=", "Partners"]], None, 1)
        partner_directory = self.env["document.directory"].search([["name", "=", partner_directory_name]], None, 1)
        if not partner_directory:
            partner_directory = self.env["document.directory"].create({
                "name": partner_directory_name,
                "model_directory": True,
                "root_directory": False,
                "parent_id": partners_directory.id,
                "active": True
            })
        print(partner_directory.id)
        # self.directory_id_mf = partner_directory.id
        return partner_directory

    @directory_id_mf.setter
    def directory_id_mf(self, directory_id):
        self._directory_id_mf = directory_id
        # self.write({
        #     "_directory_id_mf": directory_id
        # })

    @api.model
    def create(self, vals):
        vals["_directory_id_mf"] = self.directory_id_mf.id
        return super(ResPartner, self).create(vals=vals)
