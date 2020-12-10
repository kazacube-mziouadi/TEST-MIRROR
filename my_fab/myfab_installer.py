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

    def open_wizard(self, cr, uid, context=None):
        return {
            'name': _("MyFab Pre-Install Config"),
            'view_mode': 'form',
            'res_model': 'wizard.partner.import.intuiz.result.mf',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
