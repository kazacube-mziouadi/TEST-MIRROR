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
    mf_sim_action_parent = fields.Many2one("xml.import.processing.sim.action", string="Parent simulation element",
                                           ondelete="cascade")
    mf_sim_action_children = fields.One2many("xml.import.processing.sim.action", "mf_sim_action_parent",
                                             string="Children simulation elements")
