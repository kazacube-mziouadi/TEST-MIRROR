# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class ResPartner(models.Model):
    # Inherits res.partner
    _inherit = "res.partner"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    directory_id_mf = fields.Many2one("document.directory", string="Directory")

    def create_directory(self):
        if self.directory_id_mf:
            return self.directory_id_mf
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
            # TODO: Associer l'id du directory au partner
            # self.write({
            #     "directory_id_mf": partner_directory.id,
            # })
        return partner_directory

    def put_documents_in_current_directory(self):
        self.directory_id.put_documents(self.partner_doc_ids())

    def index_documents_in_current_directory(self):
        # TODO: put file in BDD
        pass


    @api.model
    def create(self, vals):
        vals["directory_id_mf"] = self.create_directory.id
        return super(ResPartner, self).create(vals=vals)

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).create(vals=vals)
        if "directory_id_mf" in vals:
            self.put_documents_in_current_directory()
        return res
