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

    def execute_simple(self, cr, uid, context=None):
        print("EXECUTE SIMPLE")
        # modules = self.pool.get('ir.module.module')
        # wizards = self.pool.get('ir.actions.todo')
        # wiz = wizards.browse(cr, uid, ref('myfab.installer.myfab_configuration_installer_todo'))
        # wiz.state = 'open'
