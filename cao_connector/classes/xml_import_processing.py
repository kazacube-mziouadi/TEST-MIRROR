# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class xml_import_processing(models.Model):
    _inherit = "xml.import.processing"

    # ===========================================================================
    # FIELDS
    # ===========================================================================
    mf_imported_from_simulation = fields.Boolean(string="Imported from simulation", default=False)

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
            self.wkf_processing_done()
        else:
            super(xml_import_processing, self).file_analyse()

    def import_simulation_lines(self):
        for simulation_line_id in self.processing_simulate_action_ids:
            simulation_line_id.process_data_import()

    @api.multi
    def wkf_processing_wait(self):
        self.write({"mf_imported_from_simulation": False})
        return super(xml_import_processing, self).wkf_processing_wait()

    @api.multi
    def wkf_processing_done(self):
        if self.state == "sim":
            self.write({"state": "done", "error_message": "", "mf_imported_from_simulation": True})
            return True
        else:
            return super(xml_import_processing, self).wkf_processing_done()

    @api.multi
    def clear_history(self, history):
        self.processing_simulate_action_ids.unlink()
        super(xml_import_processing, self).clear_history(history)
