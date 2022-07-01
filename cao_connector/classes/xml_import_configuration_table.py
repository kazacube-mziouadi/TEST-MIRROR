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
        Simulate import of xml file. Return a dictionary of simulate action.
        """
        self.set_history_list_for_data_list(data_dicts_list, data_elements_ids_list, history_list, True)

    def set_history_list_for_data_list(self, data_dicts_list, data_elements_ids_list, history_list, is_root=False):
        data_elements_to_process_ids = filter(
            lambda data_elem_id: data_dicts_list[data_elem_id]["object_relation"].is_root_beacon_relation(),
            data_elements_ids_list
        ) if is_root else filter(
            lambda data_elem_id: not data_dicts_list[data_elem_id]["object_relation"].is_root_beacon_relation(),
            data_elements_ids_list
        )
        for data_element_id in data_elements_to_process_ids:
            # Object is internal number of data
            update_tag = False
            existing_object = False
            data_dict = data_dicts_list[data_element_id]
            beacon_rc = data_dict["object_relation"]
            children_list = []
            for key in data_dict:
                if key == "Childrens_list" and data_dict["Childrens_list"]:
                    children_ids_list = data_dict["Childrens_list"].keys()
                    self.set_history_list_for_data_list(
                        data_dicts_list, children_ids_list, children_list
                    )
                    if is_root:
                        self.pop_ids_from_ids_list(children_ids_list, data_elements_ids_list)
                if key not in ["Childrens_list", "object_relation"]:
                    current_value = data_dict[key][0]
                    if type(current_value) not in [str, unicode]:
                        field_rc = self.env["ir.model.fields"].search(
                            [("model_id", "=", beacon_rc.relation_openprod_id.id), ("name", "=", key)]
                        )
                        history_list.append(self.get_creation_tuple(("unmodified", field_rc.relation, data_dict[key][0]), children_list))

            if beacon_rc.domain and beacon_rc.domain != "[]":
                research_domain = self.research_domain_converter(beacon_rc.domain, data_dict, beacon_rc, data_dicts_list)
                existing_object = self.env[beacon_rc.relation_openprod_id.model].search(research_domain)
                # print("****")
                # print(research_domain)
                # print(existing_object)
                if beacon_rc.update_object and existing_object:
                    if len(existing_object) == 1:
                        for key in data_dict:
                            if key not in ["Childrens_list", "object_relation"] and not update_tag and (
                                    data_dict[key] != existing_object[key]
                            ):
                                history_list.append(
                                    ("update", beacon_rc.relation_openprod_id.model, existing_object.id)
                                )
                                update_tag = True
                        if not update_tag:
                            history_list.append(
                                ("unmodified", beacon_rc.relation_openprod_id.model, existing_object.id)
                            )
                    else:
                        history_list.append(self.get_creation_tuple(("error", beacon_rc.relation_openprod_id.model, False), children_list))

            if beacon_rc.beacon_type != "neutral" and beacon_rc.create_object and not existing_object:
                history_list.append(self.get_creation_tuple(("create", beacon_rc.relation_openprod_id.model, False), children_list))

    @staticmethod
    def pop_ids_from_ids_list(ids_to_pop, ids_list):
        for id_to_pop in ids_to_pop:
            del ids_list[ids_list.index(id_to_pop)]

    @staticmethod
    def get_creation_tuple(current_tuple, children_list):
        if children_list:
            current_tuple_list = list(current_tuple)
            current_tuple_list.append(children_list)
            return tuple(current_tuple_list)
        else:
            return current_tuple

    def research_domain_converter(self, domain, vals, field_rc, data_dicts_list=[]):
        """
        OVERWRITE OPP
        Convertie le domain en domain de recherche utilisable par l'objet "xml_import_configuration_table"
        @param domain: Chaine de caractère
        @param vals: Structure qui contient les valeurs
        @return: Un tableau, qui contient le domaine de recherche utilisable par l'objet.
        """
        new_domain = []
        eval_domain = json.loads(domain)
        print("***")
        print(domain)
        print(vals)
        model_id = vals["object_relation"].relation_openprod_id
        for cond in eval_domain:
            field_id = self.env["ir.model.fields"].search([("model_id", "=", model_id.id), ("name", "=", cond[0])])
            value = cond[2]
            if field_id.relation and not value:
                value = self.get_child_record_id_value_for_relation_field_condition(field_id, vals, data_dicts_list)
            if cond == '|':
                new_domain.append('|')
            else:
                if 'fields' in vals.keys() and cond[0] in vals['fields']:
                    new_domain.append((cond[0], cond[1], vals['fields'][cond[0]][0]))
                elif cond[0] in vals:
                    new_domain.append((cond[0], cond[1], vals[cond[0]][0]))
                else:
                    new_domain.append((cond[0], cond[1], value))
        print(new_domain)
        return new_domain

    def get_child_record_id_value_for_relation_field_condition(self, field_id, data_dict, data_dicts_list):
        for key in data_dict["Childrens_list"]:
            if data_dict["Childrens_list"][key][0].relation_openprod_field_id == field_id:
                child_data_dict = data_dicts_list[key]
                child_record_id = self.env[field_id.model_id.name].search(
                    self.research_domain_converter(
                        child_data_dict["object_relation"].domain,
                        child_data_dict,
                        child_data_dict["object_relation"],
                        data_dicts_list,
                    )
                )
                return child_record_id.id
