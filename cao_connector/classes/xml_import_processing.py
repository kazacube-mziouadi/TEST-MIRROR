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
