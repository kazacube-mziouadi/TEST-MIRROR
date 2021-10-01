from openerp import models, fields, api, _
import copy


class MyFabInterfaceMF(models.AbstractModel):
    _name = "myfab.interface.mf"
    _auto = False
    _description = "MyFab interface abstract - To use it add to the inheriter model a model_dictionaries_to_export_mf " \
                   "One2many field targeting a model inheriting from model.dictionary.mf"

    # ===========================================================================
    # METHODS - EXPORT INTERFACE
    # ===========================================================================

    def format_models_to_export_to_dict(self):
        content_dict = []
        for model_dictionary in self.model_dictionaries_to_export_mf:
            model_name = model_dictionary.model_to_export_mf.model
            content_dict.append({
                "model_name": model_name,
                "records_list": model_dictionary.get_list_of_records_to_export()
            })
        return content_dict

    def format_models_to_import_to_dict(self):
        selected_models_dict = self.format_models_to_export_to_dict()
        json_content_array = []
        for model_object in selected_models_dict:
            model_name = model_object["model_name"]
            for record_dict in model_object["records_list"]:
                json_content_array.append({
                    "method": "create_recursive",
                    "model": model_name,
                    "fields": record_dict
                })
        return json_content_array

    # ===========================================================================
    # METHODS - IMPORT INTERFACE
    # ===========================================================================

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
            # If o2ms/m2ms need creation : we have to create them after the record's creation (required)
            self.create_nonexistent_members_in_one2manys(record_created.id, model_name, record_fields_pristine)
            return record_created
        elif orm_method_name in ["search", "write"]:
            # "Search" ORM method takes an list of tuples
            record_fields = [(key, '=', value) for key, value in record_fields.items()]
            record_found = self.env[model_name].search(record_fields, None, 1)
            if orm_method_name == "search":
                return record_found
            orm_method_on_model = getattr(record_found, orm_method_name)
            if record_fields_to_write:
                orm_method_on_model(record_fields_to_write)
            else:
                orm_method_on_model()
            return record_found

    # Set all the relation fields in the dict to the id of the matching record.
    # If this record doesn't exist and create_recursive is True, the record is created.
    # If o2ms/m2ms need creation : we will create them after their reverse m2o's creation (required)
    def set_relation_fields_to_ids(self, record_model_name, record_fields_dict, create_recursive):
        for field_name in record_fields_dict:
            if type(record_fields_dict[field_name]) is dict:
                # Many2one case : we get the id of the related record
                relation_field_id = self.set_relation_field_to_id(
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
                for one2many_member in record_fields_dict[field_name]:
                    relation_field_id = self.set_relation_field_to_id(
                        record_model_name,
                        field_name,
                        one2many_member,
                        create_recursive
                    )
                    if relation_field_id:
                        list_of_one2many_ids.append(relation_field_id)
                record_fields_dict[field_name] = list_of_one2many_ids

    # Returns the id of the record corresponding to the given relation field dictionary.
    # If no id is found and create_recursive is True and the relation field is not a one2many, the record is created.
    # Else returns False.
    def set_relation_field_to_id(self, parent_model_name, field_name, relation_field_dict, create_recursive=False):
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
        return relation_field_record.id if relation_field_record else False

    def create_nonexistent_members_in_one2manys(self, record_id, record_model_name, fields_dict):
        for field_name in fields_dict:
            if type(fields_dict[field_name]) is list:
                self.create_nonexistent_members_in_a_one2many(record_id, record_model_name, field_name,
                                                              fields_dict[field_name])

    def create_nonexistent_members_in_a_one2many(self, record_id, record_model_name, field_name, one2many_list):
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
            relation_field_dict_tuples = [(key, '=', value) for key, value in record_fields_linked_to_ids.items()]
            relation_field_record = self.env[one2many_field.relation].search(relation_field_dict_tuples, None, 1)
            if not relation_field_record:
                record_fields_linked_to_ids[one2many_field.relation_field] = record_id
                record_created = self.env[one2many_field.relation].create(record_fields_linked_to_ids)
                self.create_nonexistent_members_in_one2manys(record_created.id, one2many_field.relation,
                                                             one2many_member_dict)