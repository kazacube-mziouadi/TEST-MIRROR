# -*- coding: utf-8 -*-
from openerp import models, api, fields, _

FIELD_SEQUENCES_DICT = {
    "product_id": 1,
    "quantity": 2,
}


class xml_import_processing_sim_action(models.Model):
    _inherit = "xml.import.processing.sim.action"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Node value", compute="_compute_mf_node_value")
    mf_sequence = fields.Integer(string="Sequence", required=True, default=10)
    mf_beacon_id = fields.Many2one("xml.import.beacon.relation", string="Beacon relation", readonly=True)
    mf_field_setter_id = fields.Many2one("mf.field.setter", string="Field setter",
                                         help="Value to set non-relational field with at simulation's validation.")
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
    @api.multi
    def write(self, vals):
        if self.type == "unmodified":
            vals["mf_selected_for_import"] = False
        if self.type == "unmodified" or "mf_selected_for_import" not in vals or (
            not self.mf_selected_for_import and self.at_least_one_child_is_checked()
        ):
            return super(xml_import_processing_sim_action, self).write(vals)
        else:
            if self.mf_selected_for_import and not self.at_least_one_child_is_checked():
                vals["mf_selected_for_import"] = False
            res = super(xml_import_processing_sim_action, self).write(vals)
            self.toggle_mf_selected_for_import(triggered_by_write=True)
            return res

    def at_least_one_child_is_checked(self):
        for sim_action_child_id in self.mf_tree_view_sim_action_children_ids:
            if sim_action_child_id.mf_selected_for_import:
                return True
        return False

    @api.model
    def _processing_type_get(self):
        return super(xml_import_processing_sim_action, self)._processing_type_get() + [("delete", _("Delete"))]

    @api.one
    def _compute_mf_node_value(self):
        if self.mf_field_setter_id:
            self.name = self.mf_field_setter_id.mf_value
        else:
            record_name = self.get_node_record_name()
            self.name = record_name if record_name else _("(unnamed)")

    @api.one
    def _compute_mf_node_name(self):
        if self.mf_field_setter_id:
            self.mf_node_name = self.mf_field_setter_id.mf_field_to_set_id.field_description
        else:
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

    def toggle_mf_selected_for_import(self, triggered_by_write=False, is_child=False):
        sim_action_parent_id = self.mf_tree_view_sim_action_parent_id
        if not triggered_by_write and not is_child:
            self.mf_selected_for_import = not self.mf_selected_for_import
        elif is_child:
            self.mf_selected_for_import = sim_action_parent_id.mf_selected_for_import
        if (self.mf_selected_for_import and sim_action_parent_id and not sim_action_parent_id.mf_selected_for_import) or (
            not self.mf_selected_for_import and sim_action_parent_id and not sim_action_parent_id.at_least_one_child_is_checked()
        ):
            self.check_parent_mf_selected_for_import_recursively(self.mf_selected_for_import)
        for sim_action_child_id in self.mf_tree_view_sim_action_children_ids:
            if sim_action_child_id.mf_selected_for_import != self.mf_selected_for_import:
                sim_action_child_id.toggle_mf_selected_for_import(is_child=True)

    def check_parent_mf_selected_for_import_recursively(self, is_selected):
        sim_action_parent_id = self.mf_tree_view_sim_action_parent_id
        if sim_action_parent_id and (
            is_selected or (not is_selected and not sim_action_parent_id.at_least_one_child_is_checked())
        ):
            sim_action_parent_id.mf_selected_for_import = is_selected
            sim_action_parent_id.check_parent_mf_selected_for_import_recursively(is_selected)

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
                    if child_sim_action_id.mf_field_setter_id.mf_field_to_set_id.name == "name":
                        self_product_name = child_sim_action_id.mf_field_setter_id.mf_value
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
        for sim_action_child_id in self.mf_sim_action_children_ids:
            child_field_setter_id = sim_action_child_id.mf_field_setter_id
            if child_field_setter_id and child_field_setter_id.mf_field_to_set_id.name == field_name:
                return child_field_setter_id.mf_value
        return False

    def process_data_import(self):
        if self.mf_selected_for_import or self.type == "unmodified":
            if self.type in ["create", "update"]:
                fields_dict = {}
                for sim_action_child_id in self.mf_sim_action_children_ids:
                    field_setter_id = sim_action_child_id.mf_field_setter_id
                    if field_setter_id and (field_setter_id.mf_value or field_setter_id.mf_value is False):
                        fields_dict.update(sim_action_child_id.mf_field_setter_id.get_field_setter_dict())
                    elif not field_setter_id:
                        child_record_id = sim_action_child_id.process_data_import()
                        if child_record_id:
                            self.append_relation_field_child_to_fields_dict(
                                fields_dict, child_record_id, sim_action_child_id.mf_beacon_id
                            )
                if self.type == "create":
                    model_name = self.mf_beacon_id.relation_openprod_id.model
                    if not fields_dict:
                        return False
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

    def append_relation_field_child_to_fields_dict(self, fields_dict, child_record_id, beacon_id):
        field_name = beacon_id.relation_openprod_field_id.name
        field_type = beacon_id.relation_openprod_field_id.ttype
        field_value = self.get_relation_field_id_link_by_field_type(child_record_id.id, field_type)
        if field_name in fields_dict and type(fields_dict[field_name]) is list:
            fields_dict[field_name] += field_value
        else:
            fields_dict[field_name] = field_value

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

    def get_sim_action_creation_tuple(
            self, process_type, model_name, record_id, beacon_id, children_list, field_setter_id=False
    ):
        return (0, 0, self.get_sim_action_creation_dict(
                process_type, model_name, record_id, beacon_id, children_list, field_setter_id
        ))

    def get_sim_action_creation_dict(
            self, process_type, model_name, record_id, beacon_id, children_list, field_setter_id=False
    ):
        creation_dict = {
            "type": process_type,
            "mf_beacon_id": beacon_id.id,
            "mf_sim_action_children_ids": children_list
        }
        if model_name:
            creation_dict["object_model"] = self.env["ir.model"].search([("model", "=", model_name)]).id
            if record_id:
                creation_dict["reference"] = model_name + ',' + str(record_id)
            if field_setter_id:
                creation_dict["mf_field_setter_id"] = field_setter_id.id
        if field_setter_id and field_setter_id.mf_field_to_set_id.name in FIELD_SEQUENCES_DICT:
            creation_dict["mf_sequence"] = FIELD_SEQUENCES_DICT[field_setter_id.mf_field_to_set_id.name]
        elif beacon_id.relation_openprod_field_id.name in FIELD_SEQUENCES_DICT:
            creation_dict["mf_sequence"] = FIELD_SEQUENCES_DICT[beacon_id.relation_openprod_field_id.name]
        return creation_dict
