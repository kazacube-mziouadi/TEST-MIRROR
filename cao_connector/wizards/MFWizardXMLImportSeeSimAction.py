# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class MFWizardXMLImportSeeSimAction(models.Model):
    _name = "mf.wizard.xml.import.see.sim.action"
    _description = "myfab viewer wizard for xml import processing sim action"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_processing_sim_action_id = fields.Many2one("xml.import.processing.sim.action", string="Linked simulation element",
                                                  readonly=True)
    mf_selected_for_import = fields.Boolean(string="To import")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.model
    def default_get(self, fields_list):
        res = super(MFWizardXMLImportSeeSimAction, self).default_get(fields_list=fields_list)
        processing_sim_action_id = self.env[self._name].browse(self._context.get('active_id'))
        res["mf_processing_sim_action_id"] = processing_sim_action_id.id
        return res

    @api.onchange("mf_processing_sim_action_id")
    def onchange_mf_processing_sim_action_id(self):
        self.mf_selected_for_import = self.mf_processing_sim_action_id.mf_selected_for_import

    @api.one
    def action_validate(self):
        if self.mf_selected_for_import != self.mf_processing_sim_action_id.mf_selected_for_import:
            self.mf_processing_sim_action_id.toggle_mf_selected_for_import()
        # Reload view to update tree view
        return {'type': 'ir.actions.act_window_view_reload'}
