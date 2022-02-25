# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, modules


class DataInitializerMyFabMF(models.TransientModel):
    _inherit = "data.initializer.mf"
    _name = "data.initializer.myfab.mf"
