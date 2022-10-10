# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, modules


class MFDataInitializerSimulationByQuantity(models.Model):
    _inherit = "data.initializer.mf"
    _name = "mf.data.initializer.simulation.by.quantity"

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @staticmethod
    def get_file_path():
        return __file__

    def set_configurations(self):
        if not self.env["ir.sequence"].search([("code", '=', "mf.simulation.by.quantity")]):
            self.env["ir.sequence"].create({
                "name": _("myfab Simulation by quantity"),
                "code": "mf.simulation.by.quantity",
                "implementation": "standard",
                "active": True,
                "prefix": "SIM",
                "padding": 6,
                "number_increment": 1,
                "number_next_actual": 1
            })
        
    def update_configurations(self):
        field_config_ids = self.env["mf.simulation.config"].search([])
        if not field_config_ids:
            self.env["mf.simulation.config"].create({})
        else:
            field_config_ids.mf_update()

        sim_by_qty_ids = self.env["mf.simulation.by.quantity"].search([])
        if sim_by_qty_ids:
            sim_by_qty_ids.mf_fields_update()