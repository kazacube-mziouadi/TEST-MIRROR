# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class xml_import_processing_sim_action(models.Model):
    _inherit = "xml.import.processing.sim.action"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Record name", compute="_compute_mf_record_name")
    mf_beacon_id = fields.Many2one("xml.import.beacon.relation", string="Beacon relation", readonly=True)
    mf_field_setter_ids = fields.One2many("mf.field.setter", "mf_model_dictionary_id", string="Field setters",
                                          help="Values to set non-relational fields with at simulation's validation.")
    mf_sim_action_parent_id = fields.Many2one("xml.import.processing.sim.action", string="Parent simulation element",
                                              ondelete="cascade")
    mf_sim_action_children_ids = fields.One2many("xml.import.processing.sim.action", "mf_sim_action_parent_id",
                                                 string="Children simulation elements")
    mf_node_name = fields.Char(string="Node name", compute="_compute_mf_node_name")
    mf_tree_view_sim_action_parent_id = fields.Many2one("xml.import.processing.sim.action",
                                                        string="Parent simulation element", ondelete="cascade")
    mf_tree_view_sim_action_children_ids = fields.One2many("xml.import.processing.sim.action",
                                                           "mf_tree_view_sim_action_parent_id",
                                                           string="Treeview children simulation elements")
    mf_selected_for_import = fields.Boolean(string="To import", default=True)

    # ===========================================================================
    # METHODS - MODEL
    # ===========================================================================
    @api.model
    def _processing_type_get(self):
        return super(xml_import_processing_sim_action, self)._processing_type_get() + [("delete", _("Delete"))]

    @api.one
    def _compute_mf_record_name(self):
        record_name = self.get_node_record_name()
        self.name = record_name if record_name else _("(unnamed)")

    @api.one
    def _compute_mf_node_name(self):
        relation_field_id = self.mf_beacon_id.relation_openprod_field_id
        self.mf_node_name = relation_field_id.field_description if relation_field_id else self.object_model.name

    def get_node_record_name(self):
        if self.mf_beacon_id.relation_openprod_id.model == "mrp.bom":
            return self.get_bom_node_record_name()
        else:
            return self.reference.display_name if self.reference else self.get_field_setter_value_by_field_name("name")

    def get_bom_node_record_name(self):
        if self.reference:
            return self.reference.display_name
        for child_sim_action_id in self.mf_sim_action_children_ids:
            if child_sim_action_id.mf_beacon_id.relation_openprod_id.model == "product.product":
                return child_sim_action_id.get_node_record_name()
        return False

    @api.onchange("mf_selected_for_import")
    def onchange_mf_selected_for_import(self):
        self.toggle_mf_selected_for_import(triggered_by_onchange=True)

    def toggle_mf_selected_for_import(self, triggered_by_onchange=False):
        if not triggered_by_onchange:
            self.mf_selected_for_import = not self.mf_selected_for_import
        for sim_action_child_id in self.mf_tree_view_sim_action_children_ids:
            sim_action_child_id.write({"mf_selected_for_import": self.mf_selected_for_import})

    # ===========================================================================
    # METHODS - CONTROLLER
    # ===========================================================================
    def set_tree_view_sim_action_children(self, root_sim_actions_list):
        tree_view_sim_action_children_ids_list = []
        for sim_action_child_id in self.mf_sim_action_children_ids:
            tree_view_sim_action_child_link_tuple = sim_action_child_id.get_tree_view_sim_action_child_link_tuple(
                root_sim_actions_list
            )
            if tree_view_sim_action_child_link_tuple:
                tree_view_sim_action_children_ids_list.append(tree_view_sim_action_child_link_tuple)
            sim_action_child_id.set_tree_view_sim_action_children(root_sim_actions_list)
        self.mf_tree_view_sim_action_children_ids = tree_view_sim_action_children_ids_list

    def get_tree_view_sim_action_child_link_tuple(self, root_sim_actions_list):
        if self.mf_beacon_id.relation_openprod_id.model == "mrp.bom":
            return self.get_bom_tree_view_sim_action_child_link_tuple(root_sim_actions_list)
        else:
            return (4, self.id)

    def get_bom_tree_view_sim_action_child_link_tuple(self, root_sim_actions_list):
        self_product_id = None
        self_product_name = None
        # We search for the current bom sim_action product id
        for child_sim_action_id in self.mf_sim_action_children_ids:
            if child_sim_action_id.mf_beacon_id.relation_openprod_id.model == "product.product":
                product_reference = child_sim_action_id.reference
                if product_reference:
                    self_product_id = product_reference
                else:
                    self_product_name = child_sim_action_id.get_field_setter_value_by_field_name("name")
                    for field_setter_id in child_sim_action_id.mf_field_setter_ids:
                        if field_setter_id.mf_field_to_set_id.name == "name":
                            self_product_name = field_setter_id.mf_value
                break
        # If a root sim_action has the same product, then we return the root one id (manufactured product) ;
        # Else the current one id
        for root_sim_action_id in root_sim_actions_list:
            for root_child_sim_action_id in root_sim_action_id.mf_sim_action_children_ids:
                if root_child_sim_action_id.mf_beacon_id.relation_openprod_id.model == "product.product" and (
                    (self_product_id and self_product_id == root_child_sim_action_id.reference) or (
                        self_product_name and (
                            root_child_sim_action_id.get_field_setter_value_by_field_name("name") == self_product_name
                        )
                    )
                ):
                    return (4, root_sim_action_id.id)
        return (4, self.id)

    def get_field_setter_value_by_field_name(self, field_name):
        for field_setter_id in self.mf_field_setter_ids:
            if field_setter_id.mf_field_to_set_id.name == field_name:
                return field_setter_id.mf_value
        return False

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
                model_name = self.mf_beacon_id.relation_openprod_id.model
                if self.mf_beacon_id.use_onchange:
                    record_id = self.env[model_name].create_with_onchange(fields_dict)
                else:
                    record_id = self.env[model_name].create(fields_dict)
                self.reference = model_name + ',' + str(record_id.id)
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
