from openerp import models, fields, api, registry, _
import traceback
import base64
from openerp.exceptions import MissingError
import json


class MFCalledSaleOrderGenerator(models.Model):
    _name = "mf.called.sale.order.generator"
    _description = "myfab generator model of called sales order"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
