# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import base64
import csv
from io import StringIO


class WizardInstallerMF(models.TransientModel):
    _name = 'myfab.installer.mf'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    file = fields.Binary(string='File', required=False, ondelete='restrict')

    @api.model
    def trigger_wizard(self):
        pass
    
    @api.multi
    def action_validate_config(self):
        csv_file_decoded = base64.b64decode(self.file)
        csv_reader = csv.reader(csv_file_decoded.split('\n'), delimiter=',', quotechar='"')
        self.env["model.factory.mf"].create_from_array(list(csv_reader), "res.country")

