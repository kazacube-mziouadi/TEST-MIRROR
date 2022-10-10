# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
import datetime

class MFWizardSimulationFieldsList(models.TransientModel):
    _name = "mf.wizard.simulation.fields.list"

    name = fields.Char(readonly=True, required=True)
    mf_technical_name = fields.Char(string="Technical name", readonly=True, required=True)
    mf_simulation_id = fields.Many2one("mf.simulation.by.quantity", string="Simulation", readonly=True, required=True)