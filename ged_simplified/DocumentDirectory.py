# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.tools import config
from os import path


class DocumentDirectory(models.Model):
    # Inherits document.directory
    _inherit = "document.directory"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    absolute_path = fields.Char(compute='compute_absolute_path')
    absolute_path_windows = fields.Char(compute='compute_absolute_path_windows')

    @api.one
    @api.depends('full_path')
    def compute_absolute_path(self):
        self.absolute_path = path.join(self.datadir, self.full_path)

    @api.one
    @api.depends('full_path')
    def compute_absolute_path_windows(self):
        dbname = self.env.cr.dbname
        self.absolute_path_windows = config["data_dir_windows"] + '\documents\\' + dbname + '\\' + self.full_path.replace('/', '\\')

    def put_documents(self, documents):
        for document in documents:
            if document.directory_id != self:
                document.write({
                    "directory_id": self.id
                })
