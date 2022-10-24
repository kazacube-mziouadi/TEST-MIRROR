# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import copy

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
    mf_field_setter_id = fields.Many2one("mf.field.setter", string="Field setter", help="Value to set non-relational field with at simulation's validation.")
    mf_sim_action_parent_id = fields.Many2one("xml.import.processing.sim.action", string="Parent simulation element", ondelete="cascade")
    mf_sim_action_children_ids = fields.One2many("xml.import.processing.sim.action", "mf_sim_action_parent_id", string="Children simulation elements")
    mf_node_name = fields.Char(string="Node name", compute="_compute_mf_node_name")
    mf_tree_view_sim_action_parent_id = fields.Many2one("xml.import.processing.sim.action", string="Parent simulation element", ondelete="cascade")
    mf_tree_view_sim_action_children_ids = fields.One2many("xml.import.processing.sim.action", "mf_tree_view_sim_action_parent_id", string="Treeview children simulation elements")
    mf_selected_for_import = fields.Boolean(string="To import", default=True, readonly=True)

    # ===========================================================================
    # METHODS - MODEL
    # ===========================================================================
    @api.multi
    def write(self, vals):
        if self.type == "unmodified":
            vals["mf_selected_for_import"] = False
        if (
            self.type == "unmodified"
        ) or (
            "mf_selected_for_import" not in vals
        ) or (
            not self.mf_selected_for_import and self.mf_tree_view_sim_action_children_ids and self._mf_at_least_one_child_is_checked()
        ):
            # Simple write without cascade checking
            return super(xml_import_processing_sim_action, self).write(vals)
        else:
            # Write with cascade checking
            if self.mf_selected_for_import and self.mf_tree_view_sim_action_children_ids and not self._mf_at_least_one_child_is_checked():
                vals["mf_selected_for_import"] = False
            res = super(xml_import_processing_sim_action, self).write(vals)
            self._toggle_mf_selected_for_import(triggered_by_write=True)
            return res

    @api.model
    def _processing_type_get(self):
        return super(xml_import_processing_sim_action, self)._processing_type_get() + [("delete", _("Delete"))]

    @api.one
    def _compute_mf_node_value(self):
        if self.mf_field_setter_id:
            self.name = self.mf_field_setter_id.mf_value
        else:
            record_name = self._get_node_record_name()
            self.name = record_name if record_name else _("(unnamed)")

    @api.one
    def _compute_mf_node_name(self):
        if self.mf_field_setter_id:
            self.mf_node_name = self.mf_field_setter_id.mf_field_to_set_id.field_description
        else:
            relation_field_id = self.mf_beacon_id.relation_openprod_field_id
            self.mf_node_name = relation_field_id.field_description if relation_field_id else self.object_model.name

    def _mf_at_least_one_child_is_checked(self):
        for sim_action_child_id in self.mf_tree_view_sim_action_children_ids:
            if sim_action_child_id.mf_selected_for_import: 
                return True
        return False

    def _get_node_record_name(self):
        if self.mf_beacon_id.relation_openprod_id.model == "mrp.bom":
            return self._get_bom_node_record_name()
        else:
            return self.reference.display_name if self.reference else self._get_child_field_setter_value_by_field_name("name")

    def _get_bom_node_record_name(self):
        if self.reference:
            return self.reference.display_name
        for child_sim_action_id in self.mf_sim_action_children_ids:
            if child_sim_action_id.mf_beacon_id.relation_openprod_id.model == "product.product":
                return child_sim_action_id._get_node_record_name()
        return False

    def _toggle_mf_selected_for_import(self, triggered_by_write=False, is_child=False):
        sim_action_parent_id = self.mf_tree_view_sim_action_parent_id
        if not triggered_by_write and not is_child:
            self.mf_selected_for_import = not self.mf_selected_for_import
        elif is_child:
            self.mf_selected_for_import = sim_action_parent_id.mf_selected_for_import
        if (
            self.mf_selected_for_import and sim_action_parent_id and not sim_action_parent_id.mf_selected_for_import
        ) or (
            not self.mf_selected_for_import and sim_action_parent_id and self.mf_tree_view_sim_action_children_ids and not sim_action_parent_id._mf_at_least_one_child_is_checked()
        ):
            self._check_parent_mf_selected_for_import_recursively(self.mf_selected_for_import)
        for sim_action_child_id in self.mf_tree_view_sim_action_children_ids:
            if sim_action_child_id.mf_selected_for_import != self.mf_selected_for_import:
                sim_action_child_id._toggle_mf_selected_for_import(is_child=True)

    def _check_parent_mf_selected_for_import_recursively(self, is_selected):
        sim_action_parent_id = self.mf_tree_view_sim_action_parent_id
        if sim_action_parent_id and is_selected or (
            not is_selected and self.mf_tree_view_sim_action_children_ids and not sim_action_parent_id._mf_at_least_one_child_is_checked()
        ):
            sim_action_parent_id.mf_selected_for_import = is_selected
            sim_action_parent_id._check_parent_mf_selected_for_import_recursively(is_selected)

    # ===========================================================================
    # METHODS - CONTROLLER
    # ===========================================================================
    def set_tree_view_sim_action_children(self):
        tree_view_sim_action_children_ids_list = []
        for sim_action_child_id in self.mf_sim_action_children_ids:
            tree_view_sim_action_child_id = sim_action_child_id._get_tree_view_sim_action_child_id()
            if tree_view_sim_action_child_id:
                if tree_view_sim_action_child_id.type != "unmodified" and self.type == "unmodified":
                    # Case when a child is updated but the parent is unmodified : the parent must get updated
                    self.write({
                        "type": "update",
                        "mf_selected_for_import": True,
                    })
                tree_view_sim_action_children_ids_list.append((4, tree_view_sim_action_child_id.id))
            sim_action_child_id.set_tree_view_sim_action_children()
        self.mf_tree_view_sim_action_children_ids = tree_view_sim_action_children_ids_list
        if (
            self.mf_selected_for_import and self.mf_tree_view_sim_action_children_ids and not self._mf_at_least_one_child_is_checked()
        ) or (
            self.type == "create" and not self.mf_beacon_id.create_object
        ) or (
            self.type == "update" and not self.mf_beacon_id.update_object
        ):
            self.mf_selected_for_import = False

    def _get_tree_view_sim_action_child_id(self):
        if self.mf_beacon_id.relation_openprod_id.model == "mrp.bom":
            return self._get_bom_tree_view_sim_action_child_id()
        else:
            return self

    def _get_bom_tree_view_sim_action_child_id(self):
        # We search for the current bom sim_action product id
        self_product_id, self_product_name = self._get_child_product_id_and_name()
        # If a root sim_action has the same product, then we return the root one id (manufactured product) ;
        # Else the current one id
        root_sim_action_with_same_product_id = self._mf_get_manufactured_product_bom_id(self_product_id, self_product_name)
        return root_sim_action_with_same_product_id if root_sim_action_with_same_product_id else self

    def _get_child_field_setter_value_by_field_name(self, field_name):
        for sim_action_child_id in self.mf_sim_action_children_ids:
            child_field_setter_id = sim_action_child_id.mf_field_setter_id
            if child_field_setter_id and child_field_setter_id.mf_field_to_set_id.name == field_name:
                return child_field_setter_id.mf_value
        return False

    def _get_child_product_id_and_name(self):
        self_product_id = False
        self_product_name = False
        for child_sim_action_id in self.mf_sim_action_children_ids:
            if child_sim_action_id.mf_beacon_id.relation_openprod_id.model == "product.product":
                product_reference = child_sim_action_id.reference
                if product_reference:
                    self_product_id = product_reference
                else:
                    if child_sim_action_id.mf_sim_action_children_ids:
                        self_product_name = child_sim_action_id._get_child_field_setter_value_by_field_name("name")
                    elif child_sim_action_id.mf_field_setter_id.mf_field_to_set_id.name == "name":
                        self_product_name = child_sim_action_id.mf_field_setter_id.mf_value
                return self_product_id, self_product_name
        return self_product_id, self_product_name

    def _mf_get_manufactured_product_bom_id(self, product_id, product_name):
        processing_id = self._get_processing_id()
        for root_sim_action_id in processing_id.processing_simulate_action_ids:
            for root_child_sim_action_id in root_sim_action_id.mf_sim_action_children_ids:
                if root_child_sim_action_id.mf_beacon_id.relation_openprod_id.model == "product.product" and (
                    (
                        product_id and product_id == root_child_sim_action_id.reference
                    ) or (
                        product_name and root_child_sim_action_id._get_child_field_setter_value_by_field_name("name") == product_name
                    )
                ):
                    return root_sim_action_id
        return False

    def _get_processing_id(self):
        if self.processing_id:
            return self.processing_id
        else:
            return self.mf_sim_action_parent_id._get_processing_id()

    # ===========================================================================
    # METHODS - IMPORT
    # ===========================================================================
    def process_data_import(self, created_records_dict):
        if self.mf_selected_for_import:
            # Exclude from import, manufactured components whose bom import has been unselected
            if self.mf_beacon_id.relation_openprod_id.model == "mrp.bom":
                product_id, product_name = self._get_child_product_id_and_name()
                root_sim_action_with_same_product_id = self._mf_get_manufactured_product_bom_id(product_id, product_name)
                if root_sim_action_with_same_product_id and not root_sim_action_with_same_product_id.mf_selected_for_import:
                    return False
            if self.type in ["create", "update"]:
                self.reference = self._create_update_process(created_records_dict)
                if self.mf_beacon_id.relation_openprod_id.model == "mrp.bom" and self.processing_id.model_id.mf_documents_directory_id:
                    product_code = self.reference.product_id.code
                    self.processing_id.mf_import_product_document(product_code)
                return self.reference
            if self.type == "delete":
                self.reference.unlink()
        else:
            return self.reference

    def _create_update_process(self, created_records_dict):
        model_name = self.mf_beacon_id.relation_openprod_id.model
        #Copy the created records in a new dict to be able to make a delta and get the new ones
        children_created_records_dict = copy.deepcopy(created_records_dict)
        fields_dict = self._get_fields_dict(children_created_records_dict)

        if self.type == "update":
            self._update_record(self.reference, fields_dict)

        elif self.type == "create":
            if not fields_dict: 
                return False
            # In all cases except bom, checking if the record has not already been created ; if so, we update it
            # Boms are excluded, else the manufactured component is created in the root bom but not it's bom
            if model_name != "mrp.bom" and self.mf_beacon_id.relation_openprod_field_id.ttype not in ["one2many","many2many"] and model_name in children_created_records_dict:
                already_created_record_id = self.env["importer.service.mf"].search_records_by_fields_dict(
                    model_name,
                    self.env["mf.tools"].merge_two_dicts(fields_dict, {"id": children_created_records_dict[model_name]}),
                    1
                )
                if already_created_record_id:
                    # If we find it at already created with the sames fields dict and in the ids already created
                    # it is not necessary to update th record
                    #self._update_record(already_created_record_id, fields_dict)

                    # We must deleted all the children records created
                    self._delete_useless_created_records(created_records_dict, children_created_records_dict)

                    return already_created_record_id
            if self.mf_beacon_id.use_onchange:
                record_id = self.env[model_name].create_with_onchange(fields_dict)
            else:
                record_id = self.env[model_name].create(fields_dict)
            self.env["mf.tools"].add_value_to_dict(children_created_records_dict, model_name, record_id.id)
            self.reference = self.env["mf.tools"].generate_reference(model_name,record_id.id)
        #At end we must update the created record dict with the children created records
        #this permits to make the rest work
        created_records_dict.update(children_created_records_dict)
        
        return self.reference

    def _get_fields_dict(self, created_records_dict):
        fields_dict = {}
        for sim_action_child_id in self.mf_sim_action_children_ids:
            field_setter_id = sim_action_child_id.mf_field_setter_id
            if field_setter_id and (field_setter_id.mf_value or field_setter_id.mf_value is False):
                fields_dict.update(sim_action_child_id.mf_field_setter_id.get_field_setter_dict())
            elif not field_setter_id:
                child_record_id = sim_action_child_id.process_data_import(created_records_dict)
                if child_record_id:
                    self._append_relation_field_child_to_fields_dict(
                        fields_dict, 
                        child_record_id, 
                        sim_action_child_id.mf_beacon_id
                    )
        return fields_dict

    def _append_relation_field_child_to_fields_dict(self, fields_dict, child_record_id, beacon_id):
        field_name = beacon_id.relation_openprod_field_id.name
        field_type = beacon_id.relation_openprod_field_id.ttype
        field_value = self._get_relation_field_id_link_by_field_type(child_record_id.id, field_type)
        if field_name in fields_dict and type(fields_dict[field_name]) is list:
            fields_dict[field_name] += field_value
        else:
            fields_dict[field_name] = field_value

    @staticmethod
    def _get_relation_field_id_link_by_field_type(record_id, field_type):
        return record_id if field_type == "many2one" else [(4, record_id)]

    def _delete_useless_created_records(self, dict_1, dict_2):
        new_dict = self.env["mf.tools"].dicts_non_common_elements(dict_1,dict_2)
        for model_name in new_dict:
            if model_name and new_dict[model_name]:
                elements_to_delete = self.env["importer.service.mf"].search_records_by_fields_dict(
                    model_name,
                    {"id": new_dict[model_name]}
                )
            if elements_to_delete:
                elements_to_delete.unlink()

    def _update_record(self, record_id, fields_dict):
        fields_written_dict = self._write_different_fields_only(record_id, fields_dict)
        if fields_written_dict and self.mf_beacon_id.use_onchange:
            self._apply_onchanges_on_record_id(record_id, fields_written_dict)

    def _write_different_fields_only(self, record_id, fields_dict):
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
            elif not self.env["mf.tools"].are_values_equal_in_same_type(record_field_value, update_field_value):
                different_fields_dict[field_name] = update_field_value
        if different_fields_dict:
            record_id.write(different_fields_dict)
            return different_fields_dict
        return False

    @staticmethod
    def _apply_onchanges_on_record_id(record_id, fields_written_dict):
        for field_name in fields_written_dict.keys():
            for method in record_id._onchange_methods.get(field_name, ()):
                method(record_id)

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def get_sim_action_creation_tuple(self, process_type, model_name, record_id, beacon_id, children_list, field_setter_id=False):
        return (0, 0, self._get_sim_action_creation_dict(process_type, model_name, record_id, beacon_id, children_list, field_setter_id))

    def _get_sim_action_creation_dict(self, process_type, model_name, record_id, beacon_id, children_list, field_setter_id=False):
        creation_dict = {
            "type": process_type,
            "mf_beacon_id": beacon_id.id,
            "mf_sim_action_children_ids": children_list,
        }
        if model_name:
            creation_dict["object_model"] = self.env["ir.model"].search([("model", "=", model_name)]).id
            if record_id: 
                creation_dict["reference"] = self.env["mf.tools"].generate_reference(model_name,record_id)
            if field_setter_id: 
                creation_dict["mf_field_setter_id"] = field_setter_id.id
        if field_setter_id and field_setter_id.mf_field_to_set_id.name in FIELD_SEQUENCES_DICT:
            creation_dict["mf_sequence"] = FIELD_SEQUENCES_DICT[field_setter_id.mf_field_to_set_id.name]
        elif beacon_id.relation_openprod_field_id.name in FIELD_SEQUENCES_DICT:
            creation_dict["mf_sequence"] = FIELD_SEQUENCES_DICT[beacon_id.relation_openprod_field_id.name]
        
        return creation_dict
