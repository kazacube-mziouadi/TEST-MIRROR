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

    @api.multi
    def open_wizard(self):
        return {
            'name': _("MyFab Pre-Install Config"),
            'view_mode': 'form',
            'res_model': 'wizard.partner.import.intuiz.result.mf',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'where': self.where_mf, 'who': self.who_mf}
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
