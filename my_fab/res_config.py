# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class myfab_config_settings(models.Model):
    _name = 'myfab.config.settings'
    _inherit = 'res.config.settings'

    def create(self, cr, uid, values, context=None):
        id = super(myfab_config_settings, self).create(cr, uid, values, context)
        # Hack: to avoid some nasty bug, related fields are not written upon record creation.
        # Hence we write on those fields here.
        print("CREATE MYFAB")
        return id

    @api.model
    def default_get(self, fields_list):
        res = super(myfab_config_settings, self).default_get(fields_list=fields_list)
        print("DEFAULT GET MYFAB")
        return res

    def set_default_params(self, cr, uid, ids, context=None):
        """ set default sale and purchase taxes for products """
        print("SET DEFAULT PARAMS")

    def set_toto_of_myfabs(self, cr, uid, ids, context=None):
        print("SET TOTO")

    def set_default_dp(self, cr, uid, ids, context=None):
        print("SET DEFAULT DP")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
