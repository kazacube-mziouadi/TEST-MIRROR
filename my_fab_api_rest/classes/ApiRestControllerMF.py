# -*- coding: utf-8 -*-
from openerp import models, fields, api, http, _
from openerp.exceptions import ValidationError
import inspect, types, collections, operator, json
from ExceptionApiMF import ExceptionApiMF
from datetime import datetime

class ApiRestControllerMF(http.Controller):
    _debug = {}

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @http.route("/myfab/rest/<model>", auth="public", type="json", methods=["get"])
    def get_records(self, model, **kwargs):
        self.__reset_debug()

        debug = kwargs.get("debug", False)
        detail = kwargs.get("detail", False)

        my_model = http.request.env["ir.model"].search([("model", "=", model)])
        if getattr(my_model, "id", False) is False:
            return {"error" : "The '"+model+"' model does not exist."}

        # recuperation des fields
        fields = kwargs.get("fields", [])

        # recuperation des record selon les filtres
        filters = kwargs.get("filters", [])
        records = self.__filter_to_records(model, filters)

        # gestion des erreurs
        if isinstance(records, ExceptionApiMF):
            return {"error": records.message}

        # tri des record par id
        records.sort(key=lambda x: x.id)

        debug_list = self.__list_to_string(records)

        # Convertion en dictionary qui est convertible en json
        result = self.__list_record_to_dictionary(records, fields, detail)

        if debug is True:
            self._debug["debug"]["fields"] = fields
            self._debug["debug"]["result size"] = len(records)
            self._debug["debug"]["result id"] = debug_list
            self._debug["debug"]["model"] = model
            self._debug["result"] = result
            return self._debug
        else:
            return result;

    @http.route("/myfab/rest/<model>/<id>", auth="public", type="json", methods=["get"])
    def get_one_record(self, model, id, **kwargs):
        self.__reset_debug()

        debug = kwargs.get("debug", False)

        my_model = http.request.env["ir.model"].search([("model", "=", model)])
        if getattr(my_model, "id", False) is False:
            return {"error": "The '" + model + "' model does not exist."}

        # recuperation des fields
        fields = kwargs.get("fields", [])

        record = http.request.env[model].search([("id", "=", id)])
        result = self.__record_to_long_dictionary(record, fields)
        if debug is True:
            self._debug["debug"]["fields"] = fields
            self._debug["debug"]["result id"] = record.id
            self._debug["debug"]["model"] = model
            self._debug["result"] = result
            return self._debug
        else:
            return result;

    @http.route("/myfab/rest/<model>", auth="public", type="json", methods=["post"])
    def create_record(self, model, **kwargs):
        self.__reset_debug()

        # recuperation des fields
        fields = kwargs.get("fields", [])

        my_model = http.request.env["ir.model"].search([("model", "=", model)])
        if getattr(my_model, "id", False) is False:
            return {"error": "The '" + model + "' model does not exist."}

        records_in_dictionary = kwargs.get("record", [])

        if not isinstance(records_in_dictionary, list):
            records_in_dictionary = [records_in_dictionary]

        records = []
        for record_in_dictionary in records_in_dictionary:
            record = http.request.env[model].create(record_in_dictionary)
            records.append(record)

        result = self.__list_record_to_dictionary(records, fields, True)
        return result

    @http.route("/myfab/rest/<model>/<id>", auth="public", type="json", methods=["put"])
    def edit_record(self, model, id, **kwargs):
        self.__reset_debug()


        my_model = http.request.env["ir.model"].search([("model", "=", model)])
        if getattr(my_model, "id", False) is False:
            return {"error": "The '" + model + "' model does not exist."}

        record_dictionary = kwargs.get("record", [])

        record_object = http.request.env[model].search([("id", "=", id)])

        record_object.write(record_dictionary)

        result = self.__record_to_long_dictionary(record_object)
        return result

    @http.route("/myfab/rest/<model>/<id>", auth="public", type="json", methods=["delete"])
    def delete_record(self, model, id, **kwargs):
        self.__reset_debug()

        my_model = http.request.env["ir.model"].search([("model", "=", model)])
        if getattr(my_model, "id", False) is False:
            return {"error": "The '" + model + "' model does not exist."}

        record_object = http.request.env[model].search([("id", "=", id)])

        record_object.unlink()
        return "The '"+model+"' with id '"+str(id)+"' has been deleted with success."

    # transorme un/des filtre(s) en une liste de record
    # recursive 1/2
    def __filter_to_records(self, model_name, filter):
        self.__add_debug_log("__filter_to_records(model_name:"+model_name+", filter:"+json.dumps(filter)+")")

        # Si aucun filtre en renvois tous les resultats
        if filter is None or len(filter) == 0:
            results = http.request.env[model_name].search([]);
            return list(results)

        # Si c'est un filtre direct alors on renvoi les retour de l'ORM caste en list
        if "field" in filter and "comparator" in filter and "value" in filter:
            results = http.request.env[model_name].search(self.__parse_filter(filter));
            return list(results)

        # Si c'est une combinaison de sous-filtre
        elif "operator" in filter and "filters" in filter:
            results = self.__filters_to_list_record(model_name, filter)

            if isinstance(results, ExceptionApiMF):
                return results

            return list(results)

        else:
            return ExceptionApiMF("A filter must contain the fields 'field', 'comparator' and 'value' OR 'operator' and 'filters'.")

    # transorme des filtres (et, ou) en une liste de record
    # recursive 2/2
    def __filters_to_list_record(self, model_name, filters):
        self.__add_debug_log("__filters_to_list_record(model_name:" + model_name + ", filters:" + json.dumps(filters) + ")")

        first = True
        result = []
        for filter in filters["filters"]:
            temp = self.__filter_to_records(model_name, filter)

            if isinstance(temp, ExceptionApiMF):
                return temp

            if type(temp) is not list:
                if getattr(temp, "id", False) is not False:
                    temp = [temp]
                else:
                    temp = []

            # Le cas d'une premiere condition
            if first:
                first = False
                result = temp
                continue

            # On traite le cas ET, OU avec respectivement intersection, union
            if "operator" not in filters or filters["operator"] == "and":
                result = set(result).intersection(temp)
            else:
                result = self.__union_list(result, temp)
        return result


    # Convertie une liste de record en une liste de dictionnaire (court ou long)
    def __list_record_to_dictionary(self, records, fields=[], detail=False):
        self.__add_debug_log("__list_record_to_dictionary(records:" + self.__list_to_string(records) + ", detail:" + ("True" if detail else "False") + ")")
        list = []
        for record in records:
            if detail is True:
                list.append(self.__record_to_long_dictionary(record, fields))
            else:
                list.append(self.__record_to_short_dictionary(record))
        return list

    # Retourne l'url de base de l'API REST
    def __api_url(self):
        return http.request.env["ir.config_parameter"].sudo().get_param('web.base.url')+"/myfab/rest/"

    # Convertie un record en un dictionnaire court
    def __record_to_short_dictionary(self, record):
        self.__add_debug_log("__record_to_short_dictionary(record:" + str(record.id) + "["+type(record).__name__+"])")

        fields = fields = http.request.env["ir.model.fields"].search([("model", "=", type(record).__name__)])
        fields = map(lambda item: item.name, fields)
        return {
            "id" : record.id,
            "fields" : fields,
            "model" : type(record).__name__,
            "url_api" : self.__api_url() + type(record).__name__ + "/" + str(record.id),
        }

    # Convertie un record en un dictionnaire long
    # Les sous-record seront convertis en dictionnaire court
    def __record_to_long_dictionary(self, record, fields=[]):
        self.__add_debug_log("__record_to_long_dictionary(record:" + str(record.id) + "["+type(record).__name__+")")
        record_dictionary = {}
        model_fields = http.request.env["ir.model.fields"].search([("model", "=", type(record).__name__)])
        for model_field in model_fields:

            # Son afficher que les fields voulus
            if len(fields) > 0 and model_field.name not in fields:
                continue

            if (model_field.relation == False):
                value = record[model_field.name]
            else:
                if (model_field.ttype == "many2one"):
                    if (record[model_field.name].id == False):
                        value = None
                    else:
                        value = self.__record_to_short_dictionary(record[model_field.name])
                elif (model_field.ttype == "many2many" or model_field.ttype == "one2many"):
                    value = self.__list_record_to_dictionary(getattr(record, model_field.name), fields, False)
                else:
                    value = "Error: We should never reach this end !"
            record_dictionary[model_field.name] = value
        record_dictionary["url_api"] = self.__api_url() + type(record).__name__ + "/" + str(record.id),
        # record_dictionary = sorted((record_dictionary.items(), key=operator.itemgetter("id")))
        return record_dictionary

    # Parse un/des filtre(s)
    def __parse_filter(self, filter_encoded):
        filters = []
        if type(filter_encoded) is list:
            for filter in filter_encoded:
                filters.append((filter["field"], filter["comparator"], filter["value"]))
        else:
            filters.append((filter_encoded["field"], filter_encoded["comparator"], filter_encoded["value"]))
        return filters


    # Fait une union des deux listes sans faire de doublon
    def __union_list(self, list1, list2):
        final_list = list(set(list1) | set(list2))
        return final_list

    # Convertie un list de model en une string
    def __list_to_string(self, list1):
        list2 = []
        for record in list1:
            list2.append(str(record.id))
        return  "["+ ", ".join(list2) + "]"


    def __reset_debug(self):
        self._debug = {
            "debug": {
                "log": []
            },
            "result": []
        }

    def __add_debug_log(self, log):
        now = datetime.now()
        # current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        self._debug["debug"]["log"].append(str(now)+":"+log)



