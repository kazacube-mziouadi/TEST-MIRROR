# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class xml_import_beacon_relation(models.Model):
    _inherit = "xml.import.beacon.relation"

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def is_root_beacon_relation(self):
        parent_id = self.parent_id
        print("*********")
        while parent_id:
            print(parent_id.beacon_type)
            if parent_id.beacon_type != "neutral":
                return False
            parent_id = parent_id.parent_id
        return True

