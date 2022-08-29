# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class xml_import_attribute_relation(models.Model):
    _inherit = "xml.import.attribute.relation"

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.model
    def create(self, vals):
        if "beacon_id" not in vals:
            vals["beacon_id"] = False
        return super(xml_import_attribute_relation, self).create(vals)
