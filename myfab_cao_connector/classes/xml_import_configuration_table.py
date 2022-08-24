# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import json
from openerp.exceptions import ValidationError


class xml_import_configuration_table(models.Model):
    _inherit = "xml.import.configuration.table"

    # ===========================================================================
    # FIELDS
    # ===========================================================================
    mf_documents_directory_id = fields.Many2one("physical.directory.mf", string="Documents directory", ondelete="cascade",
                                                help="Directory from which the documents will be scanned and attached to the imported records")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def simulation_manager(self, data_dicts_dict, data_elements_ids_list, history_list):
        """
        OVERWRITE OPP
        Simulate import of xml file.
        """
        self.set_history_list_for_data_list(data_dicts_dict, history_list)

    def set_history_list_for_data_list(self, data_dicts_dict, history_list, all_data_dicts_dict={}, parent_id=False):
        if not all_data_dicts_dict:
            all_data_dicts_dict = data_dicts_dict
        data_dicts_to_process_dict = self.filter_data_dicts_by_parent_id(data_dicts_dict, parent_id)
        temp_history_list = []
        for data_dict_id in data_dicts_to_process_dict.keys():
            # Object is internal number of data
            existing_record = False
            data_dict = data_dicts_to_process_dict[data_dict_id]
            beacon_rc = data_dict["object_relation"]
            children_sim_action_list = []
            values_dict = {}

            if beacon_rc.domain and beacon_rc.domain != "[]":
                # Update processing case
                research_domain_list = self.research_domain_converter(
                    beacon_rc.domain, data_dict, beacon_rc, all_data_dicts_dict
                )
                self.add_parent_id_filter_domain_if_necessary(research_domain_list, beacon_rc, parent_id)
                model_name = beacon_rc.relation_openprod_id.model
                existing_record = self.env[model_name].search(research_domain_list)
                if len(existing_record) > 1:
                    raise ValidationError(
                        _("More than one record have been found : ") + str(existing_record) + _(". You must reduce the search domain ") + str(research_domain_list)
                    )

            for key in data_dict:
                if key == "Childrens_list" and data_dict["Childrens_list"]:
                    # Children processing case
                    children_data_ids_list = data_dict["Childrens_list"].keys()
                    self.set_history_list_for_data_list(
                        self.filter_data_dicts_by_ids(all_data_dicts_dict, children_data_ids_list),
                        children_sim_action_list, all_data_dicts_dict, existing_record
                    )
                    if children_sim_action_list and existing_record:
                        self.add_elements_to_delete_to_children_history_list(children_sim_action_list, existing_record)
                elif key not in ["Childrens_list", "object_relation"]:
                    # Value processing case
                    children_sim_action_list.append(self.get_non_relational_field_sim_action_id(
                        data_dict, key, existing_record, beacon_rc
                    ))

            if beacon_rc.update_object and existing_record:
                if len(existing_record) == 1:
                    # Checking if the import set new values on the existing records
                    if self.is_record_to_update(children_sim_action_list):
                        history_list.append(self.get_sim_action_creation_tuple(
                            "update", beacon_rc.relation_openprod_id.model, existing_record.id, beacon_rc,
                            children_sim_action_list
                        ))
                    else:
                        history_list.append(self.get_sim_action_creation_tuple(
                            "unmodified", beacon_rc.relation_openprod_id.model, existing_record.id, beacon_rc, children_sim_action_list
                        ))
                else:
                    history_list.append(self.get_sim_action_creation_tuple(
                        "error", beacon_rc.relation_openprod_id.model, False, beacon_rc, children_sim_action_list
                    ))

            if beacon_rc.beacon_type != "neutral" and beacon_rc.create_object and not existing_record and (
                    not self.is_values_dict_empty(values_dict) or children_sim_action_list
            ):
                history_list.append(self.get_sim_action_creation_tuple(
                    "create", beacon_rc.relation_openprod_id.model, False, beacon_rc, children_sim_action_list
                ))
            if not history_list and children_sim_action_list:
                temp_history_list += children_sim_action_list

        if not history_list and temp_history_list:
            history_list += temp_history_list

    def add_elements_to_delete_to_children_history_list(self, children_history_list, existing_record):
        children_history_sorted_list = sorted(children_history_list, key=lambda child_create_tuple: child_create_tuple[2]["mf_beacon_id"])
        children_history_sorted_list_last_index = len(children_history_sorted_list) - 1
        child_beacon_id = None
        model_existing_ids_list = []
        for child_creation_tuple in children_history_sorted_list:
            child_creation_dict = child_creation_tuple[2]
            if not child_beacon_id or child_beacon_id.id != child_creation_dict["mf_beacon_id"]:
                if child_beacon_id and child_beacon_id.relation_openprod_field_id.ttype != "many2one":
                    self.append_delete_element_to_history_list_if_not_checked(
                        children_history_list,
                        getattr(existing_record, child_beacon_id.relation_openprod_field_id.name),
                        model_existing_ids_list,
                        child_beacon_id
                    )
                child_beacon_id = self.env["xml.import.beacon.relation"].search([
                    ("id", '=', child_creation_dict["mf_beacon_id"])
                ])
                model_existing_ids_list = []
            if "reference" in child_creation_dict.keys():
                model_existing_ids_list.append(child_creation_dict["reference"].split(',')[1])
            if children_history_sorted_list.index(child_creation_tuple) == children_history_sorted_list_last_index and (
                    child_beacon_id and child_beacon_id.relation_openprod_field_id.ttype != "many2one"
            ):
                self.append_delete_element_to_history_list_if_not_checked(
                    children_history_list,
                    getattr(existing_record, child_beacon_id.relation_openprod_field_id.name),
                    model_existing_ids_list,
                    child_beacon_id
                )

    def append_delete_element_to_history_list_if_not_checked(self, history_list, one2many_list, checked_ids_list, beacon_id):
        for child_id in one2many_list:
            if str(child_id.id) not in checked_ids_list:
                history_list.append(self.get_sim_action_creation_tuple(
                    "delete", beacon_id.relation_openprod_id.model, child_id.id, beacon_id, []
                ))

    def get_non_relational_field_sim_action_id(self, data_dict, field_name, existing_record, beacon_id):
        model_id = self.env["ir.model"].search([("model", '=', existing_record._name)], None, 1)
        field_id = self.env["ir.model.fields"].search([
            ("name", '=', field_name),
            ("model_id", '=', model_id.id)
        ], None, 1)
        value = data_dict[field_name][0]
        if type(value) is not str and not isinstance(value, unicode):
            value = str(value)
        field_setter_id = self.env["mf.field.setter"].create({
            "mf_field_to_set_id": field_id.id,
            "mf_value": value
        })
        field_process_type = self.get_non_relational_field_process_type(existing_record, field_setter_id)
        return self.get_sim_action_creation_tuple(
            field_process_type, model_id.model, existing_record.id, beacon_id, [], field_setter_id
        )

    def get_non_relational_field_process_type(self, existing_record, field_setter_id):
        if self.env["mf.tools"].are_values_equal_in_same_type(
                getattr(existing_record, field_setter_id.mf_field_to_set_id.name), field_setter_id.mf_value
        ):
            return "unmodified"
        else:
            return "update" if existing_record else "create"

    def is_record_to_update(self, children_sim_action_list):
        return self.is_at_least_one_child_modified(children_sim_action_list)

    def is_at_least_one_child_modified(self, children_sim_action_list):
        for child_sim_action_creation_tuple in children_sim_action_list:
            child_sim_action_values_dict = child_sim_action_creation_tuple[2]
            if child_sim_action_values_dict["type"] != "unmodified" or self.is_at_least_one_child_modified(
                child_sim_action_values_dict["mf_sim_action_children_ids"]
            ):
                return True
        return False

    def filter_data_dicts_by_parent_id(self, data_dicts_dict, parent_id):
        filtered_data_dicts_dict = {}
        if parent_id is False:
            for data_dict_id in data_dicts_dict.keys():
                data_dict = data_dicts_dict[data_dict_id]
                if self.is_root_data_dict(data_dict_id, data_dict, data_dicts_dict):
                    filtered_data_dicts_dict[data_dict_id] = data_dict
        else:
            for data_dict_id in data_dicts_dict.keys():
                data_dict = data_dicts_dict[data_dict_id]
                if not self.is_root_data_dict(data_dict_id, data_dict, data_dicts_dict):
                    filtered_data_dicts_dict[data_dict_id] = data_dict
        return filtered_data_dicts_dict

    @staticmethod
    def filter_data_dicts_by_ids(data_dicts_dict, ids_list):
        filtered_data_dicts_dict = {}
        for data_dict_id in data_dicts_dict.keys():
            if data_dict_id in ids_list:
                filtered_data_dicts_dict[data_dict_id] = data_dicts_dict[data_dict_id]
        return filtered_data_dicts_dict

    def is_root_data_dict(self, data_dict_id, data_dict, data_dicts_dict):
        return data_dict["object_relation"].is_root_beacon_relation() and not self.is_id_in_another_data_children_list(
            data_dict_id, data_dicts_dict
        )

    @staticmethod
    def is_id_in_another_data_children_list(data_id, data_dicts_dict):
        for data_dict_id in data_dicts_dict.keys():
            if data_id in data_dicts_dict[data_dict_id]["Childrens_list"].keys() and (
                    data_dicts_dict[data_dict_id]["object_relation"].beacon_type != "neutral"
            ):
                return True
        return False

    def get_sim_action_creation_tuple(self, process_type, model_name, record_id, beacon_id, children_list, field_setter_id=False):
        return self.env["xml.import.processing.sim.action"].get_sim_action_creation_tuple(
            process_type, model_name, record_id, beacon_id, children_list, field_setter_id
        )

    def research_domain_converter(self, domain, data_dict, field_rc, data_dicts_dict=[]):
        """
        OVERWRITE OPP
        Convertie le domain en domain de recherche utilisable par l'objet "xml_import_configuration_table"
        @param domain: Chaine de caractères
        @param data_dict: Structure qui contient les valeurs
        @return: Un tableau, qui contient le domaine de recherche utilisable par l'objet.
        """
        if not data_dicts_dict:
            # OPP original processing (for not simulated import)
            return super(xml_import_configuration_table, self).research_domain_converter(domain, data_dict, field_rc)
        new_domain = []
        eval_domain = json.loads(domain)
        model_id = data_dict["object_relation"].relation_openprod_id
        for cond in eval_domain:
            field_id = self.env["ir.model.fields"].search([("model_id", "=", model_id.id), ("name", "=", cond[0])])
            value = cond[2]
            if field_id.relation and not value and value is not False:
                value = self.get_child_record_id_value_for_relation_field_condition(
                    field_id, data_dict, data_dicts_dict
                )
            if cond == '|':
                new_domain.append('|')
            else:
                if 'fields' in data_dict.keys() and cond[0] in data_dict['fields']:
                    new_domain.append((cond[0], cond[1], data_dict['fields'][cond[0]][0]))
                elif cond[0] in data_dict:
                    new_domain.append((cond[0], cond[1], data_dict[cond[0]][0]))
                elif value is not None:
                    new_domain.append((cond[0], cond[1], value))
        return new_domain

    def add_parent_id_filter_domain_if_necessary(self, domains_list, record_sim_action_id, parent_id):
        parent_id_relation_field_id = self.env["mf.tools"].mf_get_reverse_field_id(
            record_sim_action_id.relation_openprod_field_id
        )
        if parent_id_relation_field_id:
            domains_list.append((parent_id_relation_field_id.name, '=', parent_id.id if parent_id else False))

    def get_child_record_id_value_for_relation_field_condition(self, field_id, data_dict, data_dicts_dict):
        for child_data_id in data_dict["Childrens_list"]:
            if data_dict["Childrens_list"][child_data_id][0].relation_openprod_field_id == field_id:
                child_data_dict = data_dicts_dict[child_data_id]
                child_data_beacon_relation_id = child_data_dict["object_relation"]
                search_domains_list = self.research_domain_converter(
                    child_data_beacon_relation_id.domain,
                    child_data_dict,
                    child_data_beacon_relation_id,
                    data_dicts_dict
                )
                child_record_id = self.env[child_data_beacon_relation_id.relation_openprod_id.model].search(
                    search_domains_list
                )
                return child_record_id.id

    @staticmethod
    def is_values_dict_empty(values_dict):
        for field_name in values_dict.keys():
            field_value = values_dict[field_name]
            if field_value or type(field_value) in [int, float]:
                return False
        return True
