# -*- coding: utf-8 -*-

import logging

try:
    import simplejson as json
except ImportError:
    import json     # noqa

from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)

class myfab_installer(models.TransientModel):
    _name = 'myfab.installer'
    _inherit = 'res.config.installer'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
