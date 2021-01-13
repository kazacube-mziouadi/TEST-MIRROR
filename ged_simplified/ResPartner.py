# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class ResPartner(models.Model):
    # Inherits res.partner
    _inherit = "res.partner"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    directory_id_mf = fields.Many2one("document.directory", string="Directory")

    def compute_directory(self, directory):
        self.env.cr.execute('''
                        UPDATE
                            res_partner
                        SET
                            directory_id_mf = %s
                        WHERE
                             id = %s
                    ''' % (
        directory.id, self.id))

    def create_directory(self, name=None):
        print("####ResPartner::create_directory - in")
        if self.directory_id_mf:
            return self.directory_id_mf
        if not name:
            partner_directory_name = self.name
        else:
            partner_directory_name = name
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
        self.write({
            "directory_id_mf": partner_directory.id
        })
        return partner_directory

    def put_documents_in_current_directory(self):
        print("####ResPartner::put_documents_in_current_directory - in")
        print(self.name)
        self.directory_id_mf.put_documents(self.partner_doc_ids)

    def index_documents_in_current_directory(self):
        # TODO: put file in BDD
        pass


    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals=vals)
        self.create_directory(vals["name"])
        return res

    @api.one
    def write(self, vals):
        print("####ResPartner::write - in")
        res = super(ResPartner, self).write(vals=vals)
        self.put_documents_in_current_directory()
        return res
