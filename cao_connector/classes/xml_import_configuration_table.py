# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import json
from openerp.exceptions import ValidationError


class xml_import_configuration_table(models.Model):
    _inherit = "xml.import.configuration.table"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def simulation_manager(self, data_dicts_dict, data_elements_ids_list, history_list):
        """
        OVERWRITE OPP
        Simulate import of xml file.
        """
        self.set_history_list_for_data_list(data_dicts_dict, history_list)

    def set_history_list_for_data_list(self, data_dicts_dict, history_list, all_data_dicts_dict={}, parent_id=False, ids_processed_list=[]):
        if not all_data_dicts_dict:
            all_data_dicts_dict = data_dicts_dict
        data_dicts_to_process_dict = self.filter_data_dicts_by_parent_id(data_dicts_dict, parent_id)
        temp_history_list = []
        for data_dict_id in data_dicts_to_process_dict:
            if data_dict_id in ids_processed_list:
                continue
            ids_processed_list.append(data_dict_id)
            # Object is internal number of data
            update_tag = False
            existing_object = False
            data_dict = data_dicts_to_process_dict[data_dict_id]
            beacon_rc = data_dict["object_relation"]
            children_sim_action_list = []
            values_dict = {}

            if beacon_rc.domain and beacon_rc.domain != "[]":
                # Update processing case
                research_domain = self.research_domain_converter(
                    beacon_rc.domain, data_dict, beacon_rc, all_data_dicts_dict, parent_id
                )
                model_name = beacon_rc.relation_openprod_id.model
                existing_object = self.env[model_name].search(research_domain)
                # print("**/**")
                # print(model_name)
                # print(beacon_rc.domain)
                # print(data_dict)
                # print(research_domain)
                # print(existing_object)
                if len(existing_object) > 1:
                    raise ValidationError(
                        _("More than one record have been found : ") + str(existing_object) + _(". You must reduce the search domain ") + beacon_rc.domain
                    )

            for key in data_dict:
                if key == "Childrens_list" and data_dict["Childrens_list"]:
                    # Children processing case
                    children_data_ids_list = data_dict["Childrens_list"].keys()
                    self.set_history_list_for_data_list(
                        self.filter_data_dicts_by_ids(all_data_dicts_dict, children_data_ids_list),
                        children_sim_action_list, all_data_dicts_dict, existing_object, ids_processed_list
                    )
                elif key not in ["Childrens_list", "object_relation"]:
                    # Value processing case
                    current_value = data_dict[key][0]
                    values_dict[key] = current_value
                    if type(current_value) not in [str, unicode]:
                        field_rc = self.env["ir.model.fields"].search(
                            [("model_id", "=", beacon_rc.relation_openprod_id.id), ("name", "=", key)]
                        )
                        history_list.append(self.get_sim_action_creation_dict(
                            "unmodified", field_rc.relation, data_dict[key][0], beacon_rc, children_sim_action_list
                        ))

            if beacon_rc.update_object and existing_object:
                if len(existing_object) == 1:
                    for key in data_dict:
                        if key not in ["Childrens_list", "object_relation"] and not update_tag and (
                                data_dict[key] != existing_object[key]
                        ):
                            history_list.append(self.get_sim_action_creation_dict(
                                "update", beacon_rc.relation_openprod_id.model, existing_object.id, beacon_rc, children_sim_action_list, values_dict
                            ))
                            update_tag = True
                    if not update_tag:
                        history_list.append(self.get_sim_action_creation_dict(
                            "unmodified", beacon_rc.relation_openprod_id.model, existing_object.id, beacon_rc, children_sim_action_list
                        ))
                else:
                    history_list.append(self.get_sim_action_creation_dict(
                        "error", beacon_rc.relation_openprod_id.model, False, beacon_rc, children_sim_action_list
                    ))

            if beacon_rc.beacon_type != "neutral" and beacon_rc.create_object and not existing_object and (
                    not self.is_values_dict_empty(values_dict) or children_sim_action_list
            ):
                history_list.append(self.get_sim_action_creation_dict(
                    "create", beacon_rc.relation_openprod_id.model, False, beacon_rc, children_sim_action_list, values_dict
                ))
            if not history_list and children_sim_action_list:
                temp_history_list += children_sim_action_list

        if not history_list and temp_history_list:
            history_list += temp_history_list
        return ids_processed_list

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

    def get_sim_action_creation_dict(self, process_type, model_name, record_id, beacon_id, children_list, values_dict={}):
        creation_dict = {
            "type": process_type,
            "mf_beacon_id": beacon_id.id,
            "mf_sim_action_children_ids": children_list
        }
        if model_name:
            creation_dict["object_model"] = self.env["ir.model"].search([("model", "=", model_name)]).id
            if record_id:
                creation_dict["reference"] = model_name + ',' + str(record_id)
            if values_dict:
                creation_dict["mf_field_setter_ids"] = self.env["mf.field.setter"].get_creation_tuples_list_from_field_value_couples_dict(
                    values_dict, model_name
                )
        return (0, 0, creation_dict)

    def research_domain_converter(self, domain, data_dict, field_rc, data_dicts_dict=[], parent_id=False):
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
                children_record_ids = getattr(parent_id, data_dict["object_relation"].relation_openprod_field_id.name).ids if parent_id else []
                print("***")
                print(model_id.model)
                print(field_id.name)
                print(value)
                print(parent_id)
                print(children_record_ids)
                # print(parent_id)
                # print()
                if len(children_record_ids) == 1:
                    value = children_record_ids[0]
                else:
                    value = self.get_child_record_id_value_for_relation_field_condition(
                        field_id, data_dict, data_dicts_dict, children_record_ids,
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

    def get_child_record_id_value_for_relation_field_condition(self, field_id, data_dict, data_dicts_dict, children_record_ids=[]):
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
                if children_record_ids:
                    search_domains_list += [("id", "in", children_record_ids)]
                child_record_id = self.env[child_data_beacon_relation_id.relation_openprod_id.model].search(
                    search_domains_list
                )
                # print("***")
                # print(field_id)
                # print(data_dict)
                # print(child_data_beacon_relation_id.relation_openprod_id.model)
                # print(search_domains_list)
                # print(child_record_id)
                return child_record_id.id

    @staticmethod
    def is_values_dict_empty(values_dict):
        for field_name in values_dict.keys():
            field_value = values_dict[field_name]
            if field_value or type(field_value) in [int, float]:
                return False
        return True
