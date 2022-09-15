# -*- coding: utf-8 -*-
from operator import truediv
from openerp import models, api, fields, _


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_external_id = fields.Char(string="External ID", help="ID in the external app linked to this event.", readonly=True)
    mf_scrum_parent_id = fields.Many2one("calendar.event", string="Feature", readonly=True)
    mf_scrum_children_ids = fields.One2many("calendar.event", "mf_scrum_parent_id", string="Stories", readonly=True)
    mf_type_name = fields.Char(compute="compute_mf_type_name", readonly=True)
    mf_is_scrum_type = fields.Boolean(compute="compute_mf_is_scrum_type", readonly=True)
    mf_is_start_equal_to_stop_time = fields.Boolean(compute="compute_mf_is_start_equal_to_stop_time", readonly=True)
    mf_scrum_spent_time = fields.Float(compute="compute_mf_scrum_spent_time", string="Spent time (hours)", readonly=True)
    mf_scrum_task_spent_time = fields.Float(string="Spent time on task (hours)", readonly=True)
    mf_scrum_estimated_time = fields.Float(string="Estimated time (hours)", readonly=True)
    mf_scrum_last_update = fields.Datetime(string="Scrum last update", readonly=True)

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
        # Computing the mf_scrum_spent_time if the even has scrum children (feature or story case)
        if self.mf_scrum_children_ids:
            total_scrum_children_spent_time = 0.0
            for scrum_child in self.mf_scrum_children_ids:
                if scrum_child.mf_scrum_spent_time:
                    total_scrum_children_spent_time += scrum_child.mf_scrum_spent_time
            self.mf_scrum_spent_time = total_scrum_children_spent_time
        else:
            self.mf_scrum_spent_time = self.mf_scrum_task_spent_time
