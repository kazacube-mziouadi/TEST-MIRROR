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

    def trigger_wizard(self, cr, uid, context=None):
        pass

    @api.multi
    def action_validate_config(self):
        csv_file_decoded = base64.b64decode(self.file)
        print("*********TEST*****")
        print(csv_file_decoded)
        # file = StringIO(csv_file_decoded)
        # with open(file, 'rb') as csvfile:
        csv_reader = csv.reader(csv_file_decoded.split('\n'), delimiter=',', quotechar='"')
        print("******ITERABLE*****")
        self.env["model.factory.mf"].create_from_array(list(csv_reader), "res.country")
        # print(binascii.unhexlify('%x' % self.file))

