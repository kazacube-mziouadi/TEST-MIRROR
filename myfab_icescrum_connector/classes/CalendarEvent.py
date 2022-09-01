# -*- coding: utf-8 -*-
from operator import truediv
from openerp import models, api, fields, _


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_external_id = fields.Char(string="External ID", help="ID in the external app linked to this event.")
    mf_event_feature_id = fields.Many2one("calendar.event", string="Feature")
    mf_event_stories_ids = fields.One2many("calendar.event", "mf_event_feature_id", string="Stories")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def _check_closing_date(self, cr, uid, ids, context=None):
        for event in self.browse(cr, uid, ids, context=context):
            print("AAAAAAAAAAHAHAHAHAHAHAHAHAH")
            print(event.stop_datetime)
            if not event.stop_datetime:
                return True
            else:
                super(CalendarEvent, self)._check_closing_date()