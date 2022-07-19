# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class xml_import_processing(models.Model):
    _inherit = "xml.import.processing"

    # ===========================================================================
    # FIELDS
    # ===========================================================================
    mf_imported_from_simulation = fields.Boolean(string="Imported from simulation", default=False)

    # ===========================================================================
    # METHODS - WORKFLOW
    # ===========================================================================
    @api.multi
    def wkf_processing_wait(self):
        self.write({"mf_imported_from_simulation": False})
        return super(xml_import_processing, self).wkf_processing_wait()

    @api.multi
    def wkf_processing_done(self):
        if self.state == "sim":
            self.write({"state": "done", "error_message": '', "mf_imported_from_simulation": True})
            return True
        else:
            return super(xml_import_processing, self).wkf_processing_done()

    # ===========================================================================
    # METHODS - CONTROLLER
    # ===========================================================================
    def create_simulate_import(self, history):
        """
        Create list of simulate action of import.
        """
        self.processing_simulate_action_ids = history
        # root_sim_actions_list = self.processing_simulate_action_ids
        # self.set_tree_view_sim_action_children(root_sim_actions_list)

    def set_tree_view_sim_action_children(self, root_sim_actions_list):
        for sim_action_id in self.processing_simulate_action_ids:
            sim_action_id.set_tree_view_sim_action_children(root_sim_actions_list)

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
    def clear_history(self, history):
        self.processing_simulate_action_ids.unlink()
        super(xml_import_processing, self).clear_history(history)

    @api.multi
    def analyse_simulation(self):
        return {
            "name": _("Analyse simulation"),
            "view_type": "tree",
            "view_mode": "tree",
            "search_view_id": self.env.ref("cao_connector.mf_view_tree_xml_import_processing_sim_action").id,
            "res_model": "xml.import.processing.sim.action",
            "type": "ir.actions.act_window",
            "target": "current",
            "domain": "[('processing_id', '=', " + str(self.id) + ")]",
        }