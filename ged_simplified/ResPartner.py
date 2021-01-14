# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from os import walk, path
import time
from datetime import datetime

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
        self.compute_directory(partner_directory)
        return partner_directory

    def put_documents_in_current_directory(self):
        self.directory_id_mf.put_documents(self.partner_doc_ids)

    @api.model
    def index_documents_in_current_directory(self):
        indexed_files = self.env["document.openprod"].search([["directory_id", "=", self.directory_id_mf.id]])
        indexed_files_names = map(lambda indexed_file: indexed_file.name + ('.' + indexed_file.extension if len(indexed_file.extension) > 0 else ""), indexed_files)
        directory_path = path.join(self.directory_id_mf.datadir, self.directory_id_mf.full_path)
        for root, dirs, files in walk(directory_path):
            for filename in files:
                if filename not in indexed_files_names:
                    document_path = path.join(directory_path, filename)
                    new_document = self.env["document.openprod"].compute_link_document(document_path, self.directory_id_mf)
                    #Add existing record on many2many
                    self.write({
                        "partner_doc_ids": [(4, [new_document.id])]
                    })
                    # @deprecated
                    # self.link_document(new_document)

    @api.one
    def write(self, vals):
        self.create_directory()
        res = super(ResPartner, self).write(vals=vals)
        self.put_documents_in_current_directory()
        self.index_documents_in_current_directory()
        return res

    @api.multi
    def read(self, fields, load='_classic_read'):
        res = super(ResPartner, self).read(fields, load=load)
        if len(self) == 1:
            # TODO : on ne veut réaliser l'indexation qu'une fois par accès au Partner (actuellement + de 5...)
            # TODO : tester la longueur de partner_doc_ids par rapport à la longueur de la liste des fichiers dans la directory du Partner
            # (si différence entre les deux = indexation)
            print("INDEXING")
            # self.index_documents_in_current_directory()
        return res

    # @deprecated
    def link_document(self, document):
        self.env.cr.execute('''
                               INSERT INTO res_partner_document_openprod_rel (partner_id, document_id)
                               VALUES 
                               ('%(partner_id)s','%(document_id)s')
                           ''' % ({
            "partner_id": self.id,
            "document_id": document.id
        })
                            )