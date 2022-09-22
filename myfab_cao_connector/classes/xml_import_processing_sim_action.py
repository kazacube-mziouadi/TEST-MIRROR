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
    mf_selected_for_import = fields.Boolean(string="To import", default=True, readonly=True)

    # ===========================================================================
    # METHODS - MODEL
    # ===========================================================================
    @api.multi
    def write(self, vals):
        if self.type == "unmodified":
            vals["mf_selected_for_import"] = False
        if self.type == "unmodified" or "mf_selected_for_import" not in vals or (
            not self.mf_selected_for_import and self.mf_tree_view_sim_action_children_ids and self.at_least_one_child_is_checked()
        ):
            # Simple write without cascade checking
            return super(xml_import_processing_sim_action, self).write(vals)
        else:
            # Write with cascade checking
            if self.mf_selected_for_import and self.mf_tree_view_sim_action_children_ids and not self.at_least_one_child_is_checked():
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
            return self.reference.display_name if self.reference else self.get_child_field_setter_value_by_field_name("name")

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
            not self.mf_selected_for_import and sim_action_parent_id and self.mf_tree_view_sim_action_children_ids
            and not sim_action_parent_id.at_least_one_child_is_checked()
        ):
            self.check_parent_mf_selected_for_import_recursively(self.mf_selected_for_import)
        for sim_action_child_id in self.mf_tree_view_sim_action_children_ids:
            if sim_action_child_id.mf_selected_for_import != self.mf_selected_for_import:
                sim_action_child_id.toggle_mf_selected_for_import(is_child=True)

    def check_parent_mf_selected_for_import_recursively(self, is_selected):
        sim_action_parent_id = self.mf_tree_view_sim_action_parent_id
        if sim_action_parent_id and (
            is_selected or (
                not is_selected and self.mf_tree_view_sim_action_children_ids
                and not sim_action_parent_id.at_least_one_child_is_checked()
            )
        ):
            sim_action_parent_id.mf_selected_for_import = is_selected
            sim_action_parent_id.check_parent_mf_selected_for_import_recursively(is_selected)

    # ===========================================================================
    # METHODS - CONTROLLER
    # ===========================================================================
    def set_tree_view_sim_action_children(self):
        tree_view_sim_action_children_ids_list = []
        for sim_action_child_id in self.mf_sim_action_children_ids:
            tree_view_sim_action_child_id = sim_action_child_id.get_tree_view_sim_action_child_id()
            if tree_view_sim_action_child_id:
                if tree_view_sim_action_child_id.type != "unmodified" and self.type == "unmodified":
                    # Case when a child is updated but the parent is unmodified : the parent must get updated
                    self.write({
                        "type": "update",
                        "mf_selected_for_import": True
                    })
                tree_view_sim_action_children_ids_list.append((4, tree_view_sim_action_child_id.id))
            sim_action_child_id.set_tree_view_sim_action_children()
        self.mf_tree_view_sim_action_children_ids = tree_view_sim_action_children_ids_list
        if (
            self.mf_selected_for_import and self.mf_tree_view_sim_action_children_ids
            and not self.at_least_one_child_is_checked()
        ) or (self.type == "create" and not self.mf_beacon_id.create_object) or (self.type == "update" and not self.mf_beacon_id.update_object):
            self.mf_selected_for_import = False

    def get_tree_view_sim_action_child_id(self):
        if self.mf_beacon_id.relation_openprod_id.model == "mrp.bom":
            return self.get_bom_tree_view_sim_action_child_id()
        else:
            return self

    def get_bom_tree_view_sim_action_child_id(self):
        # We search for the current bom sim_action product id
        self_product_id, self_product_name = self.get_child_product_id_and_name()
        # If a root sim_action has the same product, then we return the root one id (manufactured product) ;
        # Else the current one id
        root_sim_action_with_same_product_id = self.mf_get_manufactured_product_bom_id(self_product_id, self_product_name)
        return root_sim_action_with_same_product_id if root_sim_action_with_same_product_id else self

    def get_child_field_setter_value_by_field_name(self, field_name):
        for sim_action_child_id in self.mf_sim_action_children_ids:
            child_field_setter_id = sim_action_child_id.mf_field_setter_id
            if child_field_setter_id and child_field_setter_id.mf_field_to_set_id.name == field_name:
                return child_field_setter_id.mf_value
        return False

    def get_child_product_id_and_name(self):
        self_product_id = False
        self_product_name = False
        for child_sim_action_id in self.mf_sim_action_children_ids:
            if child_sim_action_id.mf_beacon_id.relation_openprod_id.model == "product.product":
                product_reference = child_sim_action_id.reference
                if product_reference:
                    self_product_id = product_reference
                else:
                    if child_sim_action_id.mf_sim_action_children_ids:
                        self_product_name = child_sim_action_id.get_child_field_setter_value_by_field_name("name")
                    elif child_sim_action_id.mf_field_setter_id.mf_field_to_set_id.name == "name":
                        self_product_name = child_sim_action_id.mf_field_setter_id.mf_value
                return self_product_id, self_product_name
        return self_product_id, self_product_name

    def mf_get_manufactured_product_bom_id(self, product_id, product_name):
        processing_id = self.get_processing_id()
        for root_sim_action_id in processing_id.processing_simulate_action_ids:
            for root_child_sim_action_id in root_sim_action_id.mf_sim_action_children_ids:
                if root_child_sim_action_id.mf_beacon_id.relation_openprod_id.model == "product.product" and (
                    (product_id and product_id == root_child_sim_action_id.reference) or (
                        product_name and (
                            root_child_sim_action_id.get_child_field_setter_value_by_field_name("name") == product_name
                        )
                    )
                ):
                    return root_sim_action_id
        return False

    def get_processing_id(self):
        if self.processing_id:
            return self.processing_id
        else:
            return self.mf_sim_action_parent_id.get_processing_id()

    def process_data_import(self, created_records_dict):
        if self.mf_selected_for_import:
            # Check to not import manufactured components which bom import has been unselected
            if self.mf_beacon_id.relation_openprod_id.model == "mrp.bom":
                product_id, product_name = self.get_child_product_id_and_name()
                root_sim_action_with_same_product_id = self.mf_get_manufactured_product_bom_id(product_id, product_name)
                if root_sim_action_with_same_product_id and not root_sim_action_with_same_product_id.mf_selected_for_import:
                    return False
            if self.type in ["create", "update"]:
                fields_dict = self.get_fields_dict(created_records_dict)
                model_name = self.mf_beacon_id.relation_openprod_id.model
                if self.type == "create":
                    if not fields_dict:
                        return False
                    # In all cases except bom, checking if the record has not already been created ; if so, we update it
                    # Boms are excluded, else the manufactured component is created in the root bom but not it's bom
                    if model_name != "mrp.bom" and model_name in created_records_dict:
                        already_created_record_id = self.env["importer.service.mf"].search_records_by_fields_dict(
                            model_name,
                            self.env["mf.tools"].merge_two_dicts(fields_dict, {"id": created_records_dict[model_name]}),
                            1
                        )
                        if already_created_record_id:
                            self.update_record(already_created_record_id, fields_dict)
                            return already_created_record_id
                    if self.mf_beacon_id.use_onchange:
                        record_id = self.env[model_name].create_with_onchange(fields_dict)
                    else:
                        record_id = self.env[model_name].create(fields_dict)
                    self.reference = model_name + ',' + str(record_id.id)
                    if model_name in created_records_dict:
                        created_records_dict[model_name].append(record_id.id)
                    else:
                        created_records_dict[model_name] = [record_id.id]
                elif self.type == "update":
                    self.update_record(self.reference, fields_dict)
                if model_name == "mrp.bom" and self.processing_id.model_id.mf_documents_directory_id:
                    product_code = self.reference.product_id.code
                    self.processing_id.mf_import_product_document(product_code)
                return self.reference
            if self.type == "delete":
                self.reference.unlink()
        else:
            return self.reference

    def get_fields_dict(self, created_records_dict):
        fields_dict = {}
        for sim_action_child_id in self.mf_sim_action_children_ids:
            field_setter_id = sim_action_child_id.mf_field_setter_id
            if field_setter_id and (field_setter_id.mf_value or field_setter_id.mf_value is False):
                fields_dict.update(sim_action_child_id.mf_field_setter_id.get_field_setter_dict())
            elif not field_setter_id:
                child_record_id = sim_action_child_id.process_data_import(created_records_dict)
                if child_record_id:
                    self.append_relation_field_child_to_fields_dict(
                        fields_dict, child_record_id, sim_action_child_id.mf_beacon_id
                    )
        return fields_dict

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

    def update_record(self, record_id, fields_dict):
        fields_written_dict = self.env["mf.tools"].write_different_fields_only(record_id, fields_dict)
        if fields_written_dict and self.mf_beacon_id.use_onchange:
            self.apply_onchanges_on_record_id(record_id, fields_written_dict)

    @staticmethod
    def apply_onchanges_on_record_id(record_id, fields_written_dict):
        for field_name in fields_written_dict.keys():
            for method in record_id._onchange_methods.get(field_name, ()):
                method(record_id)

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
