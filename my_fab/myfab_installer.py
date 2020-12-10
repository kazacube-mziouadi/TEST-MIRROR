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

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None: context = {}
        res = super(myfab_installer, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        print("INSTALLING")
        return res

    def execute(self, cr, uid, ids, context=None):
        self.execute_simple(cr, uid, ids, context)
        print("EXECUTING")
        return super(myfab_installer, self).execute(cr, uid, ids, context=context)

    def execute_simple(self, cr, uid, ids, context=None):
        print("EXECUTING SIMPLE")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
