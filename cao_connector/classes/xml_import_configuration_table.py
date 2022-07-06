# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import json


class xml_import_configuration_table(models.Model):
    _inherit = "xml.import.configuration.table"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def simulation_manager(self, data_dicts_list, data_elements_ids_list, history_list):
        """
        OVERWRITE OPP
        Simulate import of xml file.
        """
        self.set_history_list_for_data_list(data_dicts_list, data_elements_ids_list, history_list)

    def set_history_list_for_data_list(self, data_dicts_list, data_elements_ids_list, history_list, parent_id=False):
        data_elements_to_process_ids = filter(
            lambda data_elem_id: not data_dicts_list[data_elem_id]["object_relation"].is_root_beacon_relation(),
            data_elements_ids_list
        ) if parent_id is not False else filter(
            lambda data_elem_id: data_dicts_list[data_elem_id]["object_relation"].is_root_beacon_relation(),
            data_elements_ids_list
        )
        for data_element_id in data_elements_to_process_ids:
            # Object is internal number of data
            update_tag = False
            existing_object = False
            data_dict = data_dicts_list[data_element_id]
            beacon_rc = data_dict["object_relation"]
            children_list = []
            values_dict = {}

            if beacon_rc.domain and beacon_rc.domain != "[]":
                # Update processing case
                research_domain = self.research_domain_converter(
                    beacon_rc.domain, data_dict, beacon_rc, data_dicts_list, parent_id
                )
                # TODO : raise error if more than one existing object
                existing_object = self.env[beacon_rc.relation_openprod_id.model].search(research_domain, None, 1)

            for key in data_dict:
                if key == "Childrens_list" and data_dict["Childrens_list"]:
                    # Children processing case
                    children_data_ids_list = data_dict["Childrens_list"].keys()
                    self.set_history_list_for_data_list(
                        data_dicts_list, children_data_ids_list, children_list, existing_object
                    )
                    if not parent_id:
                        self.pop_ids_from_ids_list(children_data_ids_list, data_elements_ids_list)
                elif key not in ["Childrens_list", "object_relation"]:
                    # Value processing case
                    current_value = data_dict[key][0]
                    values_dict[key] = current_value
                    if type(current_value) not in [str, unicode]:
                        field_rc = self.env["ir.model.fields"].search(
                            [("model_id", "=", beacon_rc.relation_openprod_id.id), ("name", "=", key)]
                        )
                        history_list.append(self.get_sim_action_creation_dict(
                            "unmodified", field_rc.relation, data_dict[key][0], beacon_rc, children_list
                        ))

            if beacon_rc.update_object and existing_object:
                if len(existing_object) == 1:
                    for key in data_dict:
                        if key not in ["Childrens_list", "object_relation"] and not update_tag and (
                                data_dict[key] != existing_object[key]
                        ):
                            history_list.append(self.get_sim_action_creation_dict(
                                "update", beacon_rc.relation_openprod_id.model, existing_object.id, beacon_rc, children_list, values_dict
                            ))
                            update_tag = True
                    if not update_tag:
                        history_list.append(self.get_sim_action_creation_dict(
                            "unmodified", beacon_rc.relation_openprod_id.model, existing_object.id, beacon_rc, children_list
                        ))
                else:
                    history_list.append(self.get_sim_action_creation_dict(
                        "error", beacon_rc.relation_openprod_id.model, False, beacon_rc, children_list
                    ))

            if beacon_rc.beacon_type != "neutral" and beacon_rc.create_object and not existing_object:
                history_list.append(self.get_sim_action_creation_dict(
                    "create", beacon_rc.relation_openprod_id.model, False, beacon_rc, children_list, values_dict
                ))

    @staticmethod
    def pop_ids_from_ids_list(ids_to_pop, ids_list):
        for id_to_pop in ids_to_pop:
            if id_to_pop in ids_list:
                del ids_list[ids_list.index(id_to_pop)]

    def get_sim_action_creation_dict(self, process_type, model_name, record_id, beacon_id, children_list, values_dict={}):
        creation_dict = {
            "type": process_type,
            "mf_beacon_id": beacon_id.id,
            "mf_sim_action_children": children_list
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

    def research_domain_converter(self, domain, vals, field_rc, data_dicts_list=[], parent_id=False):
        """
        OVERWRITE OPP
        Convertie le domain en domain de recherche utilisable par l'objet "xml_import_configuration_table"
        @param domain: Chaine de caractères
        @param vals: Structure qui contient les valeurs
        @return: Un tableau, qui contient le domaine de recherche utilisable par l'objet.
        """
        if not data_dicts_list:
            # OPP original processing (for not simulated import)
            return super(xml_import_configuration_table, self).research_domain_converter(domain, vals, field_rc)
        new_domain = []
        eval_domain = json.loads(domain)
        model_id = vals["object_relation"].relation_openprod_id
        for cond in eval_domain:
            field_id = self.env["ir.model.fields"].search([("model_id", "=", model_id.id), ("name", "=", cond[0])])
            value = cond[2]
            if field_id.relation and not value:
                children_record_ids = getattr(parent_id, field_id.name).ids if parent_id else []
                if len(children_record_ids) == 1:
                    value = children_record_ids[0]
                else:
                    value = self.get_child_record_id_value_for_relation_field_condition(field_id, vals, data_dicts_list, children_record_ids)
            if cond == '|':
                new_domain.append('|')
            else:
                if 'fields' in vals.keys() and cond[0] in vals['fields']:
                    new_domain.append((cond[0], cond[1], vals['fields'][cond[0]][0]))
                elif cond[0] in vals:
                    new_domain.append((cond[0], cond[1], vals[cond[0]][0]))
                elif value is not None:
                    new_domain.append((cond[0], cond[1], value))
        return new_domain

    def get_child_record_id_value_for_relation_field_condition(self, field_id, data_dict, data_dicts_list, children_record_ids=[]):
        for key in data_dict["Childrens_list"]:
            if data_dict["Childrens_list"][key][0].relation_openprod_field_id == field_id:
                child_data_dict = data_dicts_list[key]
                child_data_beacon_relation_id = child_data_dict["object_relation"]
                search_domains_list = self.research_domain_converter(
                    child_data_beacon_relation_id.domain,
                    child_data_dict,
                    child_data_beacon_relation_id,
                    data_dicts_list
                )
                if children_record_ids:
                    search_domains_list += [("id", "in", children_record_ids)]
                child_record_id = self.env[child_data_beacon_relation_id.relation_openprod_id.model].search(
                    search_domains_list
                )
                return child_record_id.id
