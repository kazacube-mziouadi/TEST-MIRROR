# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class xml_import_processing_sim_action(models.Model):
    _inherit = "xml.import.processing.sim.action"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_field = fields.Many2one("ir.model.fields", string="Field to set")
    mf_value = fields.Char(string="Value to set", help="Value to set the non-relational field with at export.")
    mf_sim_action_parent = fields.Many2one("xml.import.processing.sim.action", string="Parent simulation element",
                                           ondelete="cascade")
    mf_sim_action_children = fields.One2many("xml.import.processing.sim.action", "mf_sim_action_parent",
                                             string="Children simulation elements")

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def get_creation_dict_from_tuple(self, creation_tuple):
        values = {}
        values["type"] = creation_tuple[0]
        if creation_tuple[2]:
            values["reference"] = creation_tuple[1] + ',' + str(creation_tuple[2])
        model_rc = self.env["ir.model"].search([("model", "=", creation_tuple[1])])
        if model_rc:
            values["object_model"] = model_rc.id
        values["processing_id"] = self.id
        if len(creation_tuple) > 3:
            values["mf_sim_action_children"] = [
                self.get_creation_dict_from_tuple(child_tuple) for child_tuple in creation_tuple[3]
            ]
        return (0, 0, values)
