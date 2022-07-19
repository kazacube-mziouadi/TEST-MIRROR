# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class xml_import_processing_sim_action(models.Model):
    _inherit = "xml.import.processing.sim.action"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_beacon_id = fields.Many2one("xml.import.beacon.relation", string="Beacon relation", readonly=True)
    mf_field_setter_ids = fields.One2many("mf.field.setter", "mf_model_dictionary_id", string="Field setters",
                                          help="Values to set non-relational fields with at simulation's validation.")
    mf_sim_action_parent_id = fields.Many2one("xml.import.processing.sim.action", string="Parent simulation element",
                                              ondelete="cascade")
    mf_sim_action_children_ids = fields.One2many("xml.import.processing.sim.action", "mf_sim_action_parent_id",
                                                 string="Children simulation elements")
    mf_first_value_to_write = fields.Char(string="First value to write", compute="_compute_mf_first_value_to_write")
    mf_reference_name = fields.Char(string="Reference name", compute="_compute_mf_reference_name")

    # ===========================================================================
    # METHODS - MODEL
    # ===========================================================================
    @api.model
    def _processing_type_get(self):
        return super(xml_import_processing_sim_action, self)._processing_type_get() + [
            ('delete', _('Delete')),
        ]

    @api.one
    def _compute_mf_first_value_to_write(self):
        if self.mf_field_setter_ids:
            self.mf_first_value_to_write = self.mf_field_setter_ids[0].get_field_value_couple_string()

    @api.one
    def _compute_mf_reference_name(self):
        if self.reference:
            self.mf_reference_name = self.reference.display_name

    # ===========================================================================
    # METHODS - CONTROLLER
    # ===========================================================================
    def process_data_import(self):
        if self.type in ["create", "update"]:
            fields_dict = {
                field_setter_id.mf_field_to_set_id.name: field_setter_id.mf_value for field_setter_id in self.mf_field_setter_ids
            }
            for sim_action_child_id in self.mf_sim_action_children_ids:
                child_record_id = sim_action_child_id.process_data_import()
                if child_record_id:
                    beacon_id = sim_action_child_id.mf_beacon_id
                    field_name = beacon_id.relation_openprod_field_id.name
                    field_type = beacon_id.relation_openprod_field_id.ttype
                    field_value = self.get_relation_field_id_link_by_field_type(child_record_id.id, field_type)
                    if field_name in fields_dict and type(fields_dict[field_name]) is list:
                        fields_dict[field_name] += field_value
                    else:
                        fields_dict[field_name] = field_value

            if self.type == "create":
                if self.mf_beacon_id.use_onchange:
                    record_id = self.env[self.mf_beacon_id.relation_openprod_id.model].create_with_onchange(fields_dict)
                else:
                    record_id = self.env[self.mf_beacon_id.relation_openprod_id.model].create(fields_dict)
                return record_id
            elif self.type == "update":
                has_written = self.write_different_fields_only(self.reference, fields_dict)
                if has_written and self.mf_beacon_id.use_onchange:
                    self.apply_onchanges_on_record_id(self.reference, self.mf_beacon_id.relation_openprod_id)
                return self.reference
        if self.type == "unmodified":
            return self.reference
        if self.type == "delete":
            self.reference.unlink()

    @staticmethod
    def get_relation_field_id_link_by_field_type(record_id, field_type):
        return record_id if field_type == "many2one" else [(4, record_id)]

    def apply_onchanges_on_record_id(self, record_id, model_id=None):
        if not model_id:
            model_id = self.env["ir.model"].search([("model", '=', record_id._name)])
        for field_id in model_id.field_id:
            for method in record_id._onchange_methods.get(field_id.name, ()):
                method(record_id)

    def write_different_fields_only(self, record_id, fields_dict):
        different_fields_dict = {}
        for field_name in fields_dict.keys():
            update_field_value = fields_dict[field_name]
            field_id = self.env["ir.model.fields"].search(
                [("model_id", "=", record_id._name), ("name", "=", field_name)]
            )
            record_field_value = getattr(record_id, field_name)
            if field_id.ttype == "many2one" and record_field_value:
                record_field_value = record_field_value.id
            if field_id.ttype in ["one2many", "many2many"]:
                update_field_value_ids_list = [update_tuple[1] for update_tuple in update_field_value]
                record_field_value_ids_list = record_field_value.ids
                if not self.env["mf.tools"].are_lists_equal(update_field_value_ids_list, record_field_value_ids_list):
                    relation_field_values_to_add_list = []
                    for update_tuple in update_field_value:
                        if update_tuple[1] not in record_field_value_ids_list:
                            relation_field_values_to_add_list.append(update_tuple)
                    different_fields_dict[field_name] = relation_field_values_to_add_list
            elif record_field_value != update_field_value:
                different_fields_dict[field_name] = update_field_value
        if different_fields_dict:
            record_id.write(different_fields_dict)
            return True
        return False