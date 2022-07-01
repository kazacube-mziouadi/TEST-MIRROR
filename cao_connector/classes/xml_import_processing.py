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
        sim_actions_to_create_list = []
        for creation_tuple in history:
            sim_actions_to_create_list.append(
                self.env["xml.import.processing.sim.action"].get_creation_dict_from_tuple(creation_tuple)
            )
        self.write({"processing_simulate_action_ids": sim_actions_to_create_list})
