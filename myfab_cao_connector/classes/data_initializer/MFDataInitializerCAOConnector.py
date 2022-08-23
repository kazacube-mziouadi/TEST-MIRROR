# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, modules
from datetime import date
import logging

logger = logging.getLogger(__name__)


class DataInitializerCAOConnectorMF(models.Model):
    _inherit = "data.initializer.mf"
    _name = "mf.data.initializer.cao.connnector"

    # ===========================================================================
    # GENERAL METHODS
    # ===========================================================================
    @staticmethod
    def get_file_path():
        return __file__

    @staticmethod
    def get_file_extension():
        return "json"
