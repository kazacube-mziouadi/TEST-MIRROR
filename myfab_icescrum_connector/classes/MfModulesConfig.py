# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class MfModulesConfig(models.Model):
    _inherit = "mf.modules.config"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_icescrum_project_name = fields.Char(string="IceScrum project's name")
    mf_icescrum_token = fields.Char(string="IceScrum user's token")
