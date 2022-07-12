# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class xml_import_processing(models.Model):
    _inherit = "xml.import.processing"

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def create_simulate_import(self, history):
        """
        Create list of simulate action of import.
        """
        self.write({"processing_simulate_action_ids": history})

    @api.multi
    def file_analyse(self):
        if self.state == "sim":
            self.import_simulation_lines()
        else:
            super(xml_import_processing, self).file_analyse()

    def import_simulation_lines(self):
        for simulation_line_id in self.processing_simulate_action_ids:
            simulation_line_id.process_data_import()
