# -*- coding: utf-8 -*-
from operator import truediv
from openerp import models, api, fields, _


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_external_id = fields.Char(string="External ID", help="ID in the external app linked to this event.")

    # ===========================================================================
    # METHODS
    # ===========================================================================
