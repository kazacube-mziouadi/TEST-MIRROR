from openerp import models, fields, api, _
import copy
import simplejson
import csv
from StringIO import StringIO
from openerp.exceptions import MissingError


class MyFabInterfaceMF(models.AbstractModel):
    _name = "myfab.interface.mf"
    _auto = False
    _description = "MyFab interface abstract - To use it add to the inheriter model a model_dictionaries_to_export_mf "\
                   "One2many field targeting a model inheriting from model.dictionary.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    file_extension_mf = fields.Selection(
        [("json", "JSON"), ("csv", "CSV"), ("txt", "TXT")], "File extension", default=("json", "JSON"), required=True
    )
    file_separator_mf = fields.Char(string="File data separator", default=",")
    file_quoting_mf = fields.Char(string="File data quoting", default='"')
    file_encoding_mf = fields.Selection(
        [("utf-8", "UTF-8"), ("cp1252", "CP1252")], "File encoding", default=("utf-8", "UTF-8"), required=True
    )

    # ===========================================================================
    # FORMAT METHODS - EXPORT INTERFACE
    # ===========================================================================

    def format_models_to_export_to_dict(self):
        content_dict = []
        for model_dictionary in self.model_dictionaries_to_export_mf:
            model_name = model_dictionary.model_to_export_mf.model
            content_dict.append({
                "model": model_name,
                "records": model_dictionary.get_list_of_records_to_export()
            })
        return content_dict

    def format_models_to_import_to_dict(self):
        selected_models_dict = self.format_models_to_export_to_dict()
        json_content_array = []
        for model_object in selected_models_dict:
            model_name = model_object["model"]
            for record_dict in model_object["records"]:
                json_content_array.append({
                    "method": "create_recursive",
                    "model": model_name,
                    "fields": record_dict
                })
        return json_content_array

    # ===========================================================================
    # PARSING METHODS - IMPORT INTERFACE
    # ===========================================================================

    @staticmethod
    def _get_records_from_json(file_content, file_name):
        return simplejson.loads(file_content)

    def _get_records_from_txt(self, file_content, file_name):
        self.file_separator_mf = "\t"
        return self._get_records_from_csv(file_content, file_name)

    def _get_records_from_csv(self, file_content, file_name):
        model_name = self.get_model_name_from_file_name(file_name)
        csv_rows = csv.reader(
            StringIO(file_content), delimiter=str(self.file_separator_mf),
            quotechar=str(self.file_quoting_mf) if self.file_quoting_mf else None
        )
        # list containing corresponding ir.model.field of each field, and a dict tree for relation fields
        # ex: [ir.model.fields(13606,), {'template_document_id': ir.model.fields(2050,)}]
        fields_list = []
        records_list = []
        # dict containing the index of the relation field to process for each depth of a root record
        # {depth: index, depth: index, ...}
        index_to_process_for_depth_dict = {}
        for csv_row_index, csv_row in enumerate(csv_rows):
            csv_row = [item.decode(self.file_encoding_mf) for item in csv_row]
            if csv_row_index == 0:
                field_names = csv_row
                fields_list = self.get_fields_by_names_list(field_names, model_name)
            else:
                record_values_dict, is_root_record, record_to_write_id = self.get_record_dict_from_values_list(
                    csv_row, fields_list
                )
                if is_root_record:
                    index_to_process_for_depth_dict = {}
                    record_to_append = {
                        "method": "write" if record_to_write_id else "create_recursive",
                        "model": model_name,
                        "fields": {"id": record_to_write_id} if record_to_write_id else record_values_dict
                    }
                    if record_to_write_id:
                        record_to_append["write"] = record_values_dict
                    records_list.append(record_to_append)
                else:
                    last_relation_field_processed_depth = self.add_relation_field_dict_to_relation_field_list(
                        record_values_dict,
                        [records_list[-1]["fields"]],
                        index_to_process_for_depth_dict
                    )
                    index_to_process_for_depth_dict[last_relation_field_processed_depth] += 1
        return records_list

    def get_fields_by_names_list(self, field_names_list, model_name):
        fields_list = []
        for field_name in field_names_list:
            fields_list.append(self.get_field_by_name_tree(field_name, model_name))
        return fields_list

    def get_field_by_name_tree(self, field_name_tree, model_name):
        model = self.env["ir.model"].search([
            ("model", '=', model_name)
        ], None, 1)
        if '/' in field_name_tree:
            field_name_tree_list = field_name_tree.split('/')
            sub_field_name_tree = self.get_sub_field_name_tree_str(field_name_tree_list)
            root_field = self.get_field_name_tree_list_root_field(field_name_tree_list, model.id)
            return {
                "field": root_field,
                "sub_field": self.get_field_by_name_tree(sub_field_name_tree, root_field.relation)
            }
        else:
            field = self.env["ir.model.fields"].search([
                ("name", '=', field_name_tree),
                ("model_id", '=', model.id)
            ], None, 1)
            return {"field": field}

    @staticmethod
    def get_sub_field_name_tree_str(field_name_tree_list):
        return '/'.join(field_name_tree_list[1:])

    def get_field_name_tree_list_root_field(self, field_name_tree_list, model_id):
        root_field_name = field_name_tree_list[0]
        root_field = self.env["ir.model.fields"].search([
            ("name", '=', root_field_name),
            ("model_id", '=', model_id)
        ], None, 1)
        return root_field

    def get_record_dict_from_values_list(self, values_list, fields_list):
        record_dict = {}
        is_root_record = False
        record_to_write_id = None
        for field_index, field_dict in enumerate(fields_list):
            if values_list[field_index] != '':
                if "sub_field" not in field_dict:
                    is_root_record = True
                    field = field_dict["field"]
                    if field.name == "id":
                        record_to_write_id = values_list[field_index]
                        continue
                self.set_field_tree_leaf_value(
                    record_dict, field_dict, values_list[field_index]
                )
        return record_dict, is_root_record, record_to_write_id

    def set_field_tree_leaf_value(self, record_tree_part, sub_field_dict, value):
        if "sub_field" in sub_field_dict:
            field = sub_field_dict["field"]
            if field.ttype == "many2one":
                if field.name not in record_tree_part:
                    record_tree_part[field.name] = {}
                self.set_field_tree_leaf_value(record_tree_part[field.name], sub_field_dict["sub_field"], value)
            else:
                if field.name not in record_tree_part:
                    record_tree_part[field.name] = [{}]
                self.set_field_tree_leaf_value(record_tree_part[field.name][0], sub_field_dict["sub_field"], value)
        else:
            field_to_fill = sub_field_dict["field"]
            if field_to_fill.ttype == "many2one":
                if field_to_fill.relation == "ir.model.fields":
                    record_tree_part[field_to_fill.name] = {"field_description": value}
                else:
                    record_tree_part[field_to_fill.name] = {"name": value}
            else:
                record_tree_part[field_to_fill.name] = value

    def add_relation_field_dict_to_relation_field_list(self, relation_field_dict, relation_field_list,
                                                       index_to_process_for_depth_dict, depth=-1):
        depth += 1
        if depth not in index_to_process_for_depth_dict:
            index_to_process_for_depth_dict[depth] = 0
        relation_field_dict_first_field_name = list(relation_field_dict.keys())[0]
        if type(relation_field_dict[relation_field_dict_first_field_name]) is list:
            return self.add_relation_field_dict_to_relation_field_list(
                relation_field_dict[relation_field_dict_first_field_name][0],
                relation_field_list[index_to_process_for_depth_dict[depth]][relation_field_dict_first_field_name],
                index_to_process_for_depth_dict,
                depth
            )
        else:
            relation_field_list.append(relation_field_dict)
            return depth

    @staticmethod
    # Returns the model name from a given import file name (the file name without the extension)
    def get_model_name_from_file_name(file_name):
        file_name_split = file_name.split('.')
        file_name_split.pop()
        return '.'.join(file_name_split)

    # ===========================================================================
    # IMPORTING METHODS - IMPORT INTERFACE
    # ===========================================================================

    def process_records_list(self, records_to_process_list):
        for record_to_process_dict in records_to_process_list:
            model_returned = self.apply_orm_method_to_model(
                record_to_process_dict["model"],
                record_to_process_dict["fields"],
                record_to_process_dict["write"] if "write" in record_to_process_dict else False,
                record_to_process_dict["method"]
            )
            if "callback" in record_to_process_dict:
                callback_method_on_model = getattr(model_returned, record_to_process_dict["callback"])
                callback_method_on_model()

    # Apply an ORM method (create/create_recursive/write/search/unlink) on the given model_name, with the given dicts :
    #     - record_fields for the fields of the record we are looking for
    #     - record_fields_to_write for the fields we want to update for the searched record (write method only)
    def apply_orm_method_to_model(self, model_name, record_fields, record_fields_to_write, orm_method_name):
        record_fields_pristine = copy.deepcopy(record_fields)
        # Retrieving the ID of each field which is an object recursively
        self.set_relation_fields_to_ids(model_name, record_fields, orm_method_name == "create_recursive")
        if record_fields_to_write:
            self.set_relation_fields_to_ids(model_name, record_fields_to_write, orm_method_name == "create_recursive")
        if orm_method_name == "create":
            record_fields["user_id"] = self.env.user.id
            return self.env[model_name].create(record_fields)
        elif orm_method_name == "create_recursive":
            record_created = self.env[model_name].create(record_fields)
            # If o2ms/m2ms members need creation : we have to create them after the record's creation (required)
            self.create_nonexistent_members_in_2manys(record_created.id, model_name, record_fields_pristine)
            return record_created
        elif orm_method_name in ["search", "write"]:
            # "Search" ORM method takes an list of tuples
            record_fields = [
                (key, 'in', value) if type(value) is list else (key, '=', value)
                for key, value in record_fields.items()
            ]
            record_found = self.env[model_name].search(record_fields, None, 1)
            if orm_method_name == "search":
                return record_found
            if not record_found:
                raise MissingError("No record found for model " + model_name + " with attributes " + str(record_fields))
            orm_method_on_model = getattr(record_found, orm_method_name)
            orm_method_on_model(record_fields_to_write)
            return record_found

    # Set all the relation fields in the dict to the id of the matching record.
    # If this record doesn't exist and create_recursive is True, the record is created.
    # If o2ms/m2ms need creation : we will create them after their reverse m2o's creation (required)
    def set_relation_fields_to_ids(self, record_model_name, record_fields_dict, create_recursive):
        for field_name in record_fields_dict:
            if type(record_fields_dict[field_name]) is dict:
                # Many2one case : we get the id of the related record
                relation_field_id, field_type = self.set_relation_field_to_id(
                    record_model_name,
                    field_name,
                    record_fields_dict[field_name],
                    create_recursive
                )
                if relation_field_id:
                    record_fields_dict[field_name] = relation_field_id
            elif type(record_fields_dict[field_name]) is list:
                # Many2many and One2many case : we get the list of ids of the related records
                list_of_one2many_ids = []
                is_list_of_many2one = False
                for one2many_member in record_fields_dict[field_name]:
                    relation_field_id, field_type = self.set_relation_field_to_id(
                        record_model_name,
                        field_name,
                        one2many_member,
                        create_recursive
                    )
                    if relation_field_id and (field_type in ["one2many", "many2many"]):
                        list_of_one2many_ids.append(relation_field_id)
                    else:
                        # TODO : dirty but most efficient way to get around the many2one as list in CSV Odoo export file
                        record_fields_dict[field_name] = relation_field_id
                        is_list_of_many2one = True
                if not is_list_of_many2one:
                    record_fields_dict[field_name] = list_of_one2many_ids

    # Returns the id of the record corresponding to the given relation field dictionary.
    # If no id is found and create_recursive is True and the relation field is not a one2many, the record is created.
    # Else returns False.
    def set_relation_field_to_id(self, parent_model_name, field_name, relation_field_dict, create_recursive=False):
        if "id" in relation_field_dict and type(relation_field_dict["id"]) is not int:
            # TODO : Odoo CSV export case => an 'id' that refers to an ir.model through the ir.model.data table
            ir_model_data_values = relation_field_dict["id"].split('.')
            ir_model_data = self.env["ir.model.data"].search([
                ("module", '=', ir_model_data_values[0]), ("name", '=', ir_model_data_values[1])
            ])
            ir_model = self.env["ir.model"].search([("model", '=', ir_model_data.model)])
            return ir_model.id, "many2one"
        if not parent_model_name:
            return False
        parent_model = self.env["ir.model"].search([
            ("model", '=', parent_model_name)
        ], None, 1)
        field_model = self.env["ir.model.fields"].search([
            ("name", '=', field_name),
            ("model_id", '=', parent_model.id)
        ], None, 1)
        self.set_relation_fields_to_ids(field_model.relation, relation_field_dict, create_recursive)
        relation_field_dict_tuples = [
            (key, 'in', value) if type(value) is list else (key, '=', value)
            for key, value in relation_field_dict.items()
        ]
        relation_field_record = self.env[field_model.relation].search(relation_field_dict_tuples, None, 1)
        if not relation_field_record and create_recursive and (field_model.ttype not in ["one2many", "many2many"]):
            # If the record linked by the relation field doesn't exist, is not a ...2many member (created later),
            # and the create_recursive argument is True, we create the field
            relation_field_record = self.apply_orm_method_to_model(
                field_model.relation,
                relation_field_dict,
                False,
                "create_recursive"
            )
        return relation_field_record.id if relation_field_record else False, field_model.ttype

    def create_nonexistent_members_in_2manys(self, record_id, record_model_name, fields_dict):
        for field_name in fields_dict:
            if type(fields_dict[field_name]) is list:
                self.create_nonexistent_members_in_a_2many(record_id, record_model_name, field_name,
                                                           fields_dict[field_name])

    def create_nonexistent_members_in_a_2many(self, record_id, record_model_name, field_name, one2many_list):
        parent_model = self.env["ir.model"].search([
            ("model", '=', record_model_name)
        ], None, 1)
        one2many_field = self.env["ir.model.fields"].search([
            ("name", '=', field_name),
            ("model_id", '=', parent_model.id)
        ], None, 1)
        for one2many_member_dict in one2many_list:
            record_fields_linked_to_ids = copy.deepcopy(one2many_member_dict)
            self.set_relation_fields_to_ids(one2many_field.relation, record_fields_linked_to_ids, True)
            relation_field_dict_tuples = [
                (key, 'in', value) if type(value) is list else (key, '=', value)
                for key, value in record_fields_linked_to_ids.items()
            ]
            relation_field_record = self.env[one2many_field.relation].search(relation_field_dict_tuples, None, 1)
            if not relation_field_record:
                record_fields_linked_to_ids[one2many_field.relation_field] = record_id
                keys_to_remove = []
                for field_name in record_fields_linked_to_ids:
                    if type(record_fields_linked_to_ids[field_name]) is list:
                        keys_to_remove.append(field_name)
                for key_to_remove in keys_to_remove:
                    record_fields_linked_to_ids.pop(key_to_remove)
                record_created = self.env[one2many_field.relation].create(record_fields_linked_to_ids)
                self.create_nonexistent_members_in_2manys(record_created.id, one2many_field.relation,
                                                          one2many_member_dict)
