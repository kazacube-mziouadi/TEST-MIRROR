# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class mf_xml_import_see_processing_sim_action(models.Model):
    _name = "mf.xml.import.see.processing.sim.action"
    _description = "myfab viewer wizard for xml import processing sim action"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_processing_sim_action_id = fields.Many2one("xml.import.processing.sim.action", string="Linked simulation element",
                                                  readonly=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.model
    def default_get(self, fields_list):
        res = super(mf_xml_import_see_processing_sim_action, self).default_get(fields_list=fields_list)
        processing_sim_action_id = self.env[self._name].browse(self._context.get('active_id'))
        res["mf_processing_sim_action_id"] = processing_sim_action_id.id
        return res