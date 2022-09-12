# -*- coding: utf-8 -*-
from operator import truediv
from openerp import models, api, fields, _


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_external_id = fields.Char(string="External ID", help="ID in the external app linked to this event.")
    mf_scrum_parent_id = fields.Many2one("calendar.event", string="Feature")
    mf_scrum_children_ids = fields.One2many("calendar.event", "mf_scrum_parent_id", string="Stories")
    mf_type_name = fields.Char(compute="compute_mf_type_name")
    mf_is_scrum_type = fields.Boolean(compute="compute_mf_is_scrum_type")
    mf_is_start_equal_to_stop_time = fields.Boolean(compute="compute_mf_is_start_equal_to_stop_time")
    mf_scrum_spent_time = fields.Float(compute="compute_mf_scrum_spent_time", string="Temps passé (heures)")
    mf_scrum_estimated_time = fields.Float(string="Temps estimé (heures)")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.one
    @api.depends("type_id")
    def compute_mf_type_name(self):
        self.mf_type_name = self.type_id.name

    @api.one
    @api.depends("type_id")
    def compute_mf_is_scrum_type(self):
        self.mf_is_scrum_type = self.type_id.name in self.env["mf.wizard.import.icescrum"].get_scrum_type_names()

    @api.one
    @api.depends("start_datetime", "stop_datetime")
    def compute_mf_is_start_equal_to_stop_time(self):
        self.mf_is_start_equal_to_stop_time = self.start_datetime == self.stop_datetime

    @api.one
    @api.depends("mf_scrum_children_ids")
    def compute_mf_scrum_spent_time(self):
        total_scrum_children_spent_time = 0.0
        for scrum_child in self.mf_scrum_children_ids:
            total_scrum_children_spent_time += scrum_child.mf_scrum_spent_time
        self.mf_scrum_spent_time = total_scrum_children_spent_time
