# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class xml_import_processing_sim_action(models.Model):
    _inherit = "xml.import.processing.sim.action"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_beacon_id = fields.Many2one("xml.import.beacon.relation", string="Beacon relation")
    mf_field_setter_ids = fields.One2many("mf.field.setter", "mf_model_dictionary_id", string="Field setters",
                                          help="Values to set non-relational fields with at simulation's validation.")
    mf_sim_action_parent_id = fields.Many2one("xml.import.processing.sim.action", string="Parent simulation element",
                                              ondelete="cascade")
    mf_sim_action_children_ids = fields.One2many("xml.import.processing.sim.action", "mf_sim_action_parent",
                                                 string="Children simulation elements")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def process_data_import(self):
        if self.type in ["create", "update"]:
            fields_dict = {
                field_setter_id.mf_field.name: field_setter_id.mf_value for field_setter_id in self.mf_field_setter_ids
            }
            for sim_action_child_id in self.mf_sim_action_children_ids:
                child_record_id = sim_action_child_id.process_data_import()
                fields_dict[sim_action_child_id.mf_beacon_id.relation_openprod_field_id.name] = [(4, child_record_id.id)]
            if self.type == "create":
                return self.env[self.mf_beacon_id.relation_openprod_id.model].create(fields_dict)
            elif self.type == "update":
                self.reference.write(fields_dict)
                return self.reference
