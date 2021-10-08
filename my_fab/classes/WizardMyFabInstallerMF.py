# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, modules
import os
import simplejson


class WizardMyFabInstallerMF(models.TransientModel):
    _inherit = "myfab.interface.mf"
    _name = "wizard.myfab.installer.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    launch_import = fields.Boolean(string='Launch import', default=False)

    @api.multi
    def trigger_wizard(self):
        pass

    @api.multi
    def import_data(self):
        data_dir_path = "/etc/openprod_home/myfab/my_fab/static/data"
        files = [f for f in os.listdir(data_dir_path) if os.path.isfile(os.path.join(data_dir_path, f))]
        for file_name in files:
            self.import_file(data_dir_path, file_name)

    def import_file(self, data_dir_path, file_name):
        file = open(os.path.join(data_dir_path, file_name), "r")
        file_content = file.read()
        records_to_process_list = simplejson.loads(file_content)
        self.process_records_list(records_to_process_list)
