from openerp import models, fields, api, _
import simplejson
import csv
from StringIO import StringIO


class ParserServiceMF(models.TransientModel):
    _name = "parser.service.mf"
    _description = "Parser service MyFab"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def get_records_from_file(
            self, file_extension, file_content, file_name, file_separator, file_quoting, file_encoding
    ):
        if file_extension == "json":
            return self.get_records_from_json(file_content)
        elif file_extension == "csv":
            return self.get_records_from_csv(file_content, file_name, file_separator, file_quoting, file_encoding)
        elif file_extension == "txt":
            return self.get_records_from_txt(file_content, file_name, file_quoting, file_encoding)
        raise ValueError("The " + file_extension + " file extension is not supported.")

    @staticmethod
    def get_records_from_json(file_content):
        return simplejson.loads(file_content)

    def get_records_from_txt(self, file_content, file_name, file_quoting, file_encoding):
        # TODO : doit-on pouvoir choisir du TXT ? (permet uniquement de mettre tabulation en separateur)
        return self.get_records_from_csv(file_content, file_name, "\t", file_quoting, file_encoding)

    def get_records_from_csv(self, file_content, file_name, file_separator, file_quoting, file_encoding):
        model_name = self.env["file.mf"].get_model_name_from_file_name(file_name)
        csv_rows = csv.reader(
            StringIO(file_content), delimiter=str(file_separator),
            quotechar=str(file_quoting) if file_quoting else None
        )
        # list containing the dicts corresponding to the root records to create
        records_list = []
        # list containing the corresponding ir.model.field of each field, and a dict tree for relation fields
        # [{'field': ir.model.fields(13606,)}, {'field': ir.model.fields(2050,), 'sub_field': {'field': ...}}]
        fields_list = []
        for csv_row_index, csv_row in enumerate(csv_rows):
            csv_row = [cell.decode(file_encoding) for cell in csv_row]
            if csv_row_index == 0:
                # First CSV line : we retrieve the names of the fields
                field_names_list = csv_row
                fields_list = self.get_fields_by_names_list(field_names_list, model_name)
            else:
                # Other CSV lines : we retrieve the values of the different records
                record_values_dict, is_root_record, record_to_write_id = self.get_record_dict_from_values_list(
                    csv_row, fields_list
                )
                row_dict = {
                    "row_number": csv_row_index,
                    "row_content": csv_row
                }
                if is_root_record:
                    # If it's a root record, we create a new dict matching the record to create
                    record_to_append = {
                        "method": "write" if record_to_write_id else "create",
                        "model": model_name,
                        "fields": {"id": record_to_write_id} if record_to_write_id else record_values_dict,
                        "rows": [row_dict]
                    }
                    if record_to_write_id:
                        record_to_append["write"] = record_values_dict
                    records_list.append(record_to_append)
                else:
                    # If it's not a root record, we add the record dict to the good part of the last root record
                    self.add_relation_field_dict_to_relation_field_list(
                        record_values_dict,
                        [records_list[-1]["fields"]]
                    )
                    records_list[-1]["rows"].append(row_dict)
        return records_list

    """
        field_names_list: a list of fields names as they are written in the CSV, in the following format :
            ["field1", "field_root/field_child", ...]
        model_name: name of the model which contains the fields
        
        Returns a list with the tree structure of the fields each linked to it's field record, in the following format :
            [{'field': ir.model.fields(13606,)}, {'field': ir.model.fields(2050,), 'sub_field': {'field': ...}}]
    """
    def get_fields_by_names_list(self, field_names_list, model_name):
        fields_list = []
        for field_name in field_names_list:
            fields_list.append(self.get_field_by_name_tree(field_name, model_name))
        return fields_list

    """
        field_name_tree: a field name as written in the CSV, in the format "field_root/field_child"
        model_name: name of the model which contains the field
        
        Returns the tree structure of the field as a dict, in the format :
            - {'field': ir.model.fields(13606,)} for a simple field.
            - {'field': ir.model.fields(2050,), 'sub_field': {'field': ...}} for a relation field.
    """
    def get_field_by_name_tree(self, field_name_tree, model_name):
        model = self.env["ir.model"].search([("model", '=', model_name)], None, 1)
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

    """
        field_name_tree_list: a list with the parts of the tree structure of one relation field, in the format :
            ["field_root", "field_child", "field_grandchild"] corresponding to "field_root/field_child/field_grandchild"
        
        Returns the children fields tree structure, so in this example : "field_child/field_grandchild"
    """
    @staticmethod
    def get_sub_field_name_tree_str(field_name_tree_list):
        return '/'.join(field_name_tree_list[1:])

    """
        field_name_tree_list: a list with the parts of the tree structure of one relation field, in the format :
            ["field_root", "field_child", "field_grandchild"] corresponding to "field_root/field_child/field_grandchild"

        Returns the root field's record from ir.model.fields
    """
    def get_field_name_tree_list_root_field(self, field_name_tree_list, model_id):
        root_field_name = field_name_tree_list[0]
        root_field = self.env["ir.model.fields"].search([
            ("name", '=', root_field_name),
            ("model_id", '=', model_id)
        ], None, 1)
        return root_field

    """
        values_list: a list with the values from the CSV line, in the format :
            ["value1", "value2", ...]
        fields_list: a list with the tree structure of the fields each linked to it's field record, in the format :
            [{'field': ir.model.fields(13606,)}, {'field': ir.model.fields(2050,), 'sub_field': {'field': ...}}]

        Returns :
        record_dict: a dict matching the fields' structure of the final record, with the values corresponding to each :
            {
                "field_string": value1,
                "field_many2one": {
                    "field_child": value2
                },
                "field_x2many": [
                    {
                        "field_child2": value3
                    }
                ]
            }       
        is_root_record: a boolean which indicates if the processed record is a root one (has no "parent" field)
        record_to_write_id: in write case only, the ID of the record on which we write 
    """
    def get_record_dict_from_values_list(self, values_list, fields_list):
        record_dict = {}
        is_root_record = False
        record_to_write_id = None
        for field_index, field_dict in enumerate(fields_list):
            if values_list[field_index] != '':
                if "sub_field" not in field_dict:
                    is_root_record = True
                    field = field_dict["field"]
                    if field.name == "id" and values_list[field_index].isdecimal():
                        record_to_write_id = values_list[field_index]
                        continue
                self.set_field_tree_leaf_value(
                    record_dict, field_dict, values_list[field_index]
                )
        return record_dict, is_root_record, record_to_write_id

    """
        record_tree_part: a dict corresponding to a part of the final dict of the record, that we will create thanks to 
            the field's tree structure
        sub_field_dict: a dict with the tree structure of the relation field in the format :
            {'field': ir.model.fields(2050,), 'sub_field': {'field': ...}}
        value: the value to set in record_tree_part at the leaf of the tree structure (at the "subbest" field)
    """
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

    """
        relation_field_dict: dict representing the sub record to add to the x2many list
        relation_field_list: list representing elements in a x2many, in which we add relation_field_dict
    """
    def add_relation_field_dict_to_relation_field_list(self, relation_field_dict, relation_field_list):
        relation_field_dict_first_field_name = list(relation_field_dict.keys())[0]
        if type(relation_field_dict[relation_field_dict_first_field_name]) is list:
            return self.add_relation_field_dict_to_relation_field_list(
                relation_field_dict[relation_field_dict_first_field_name][0],
                relation_field_list[-1][relation_field_dict_first_field_name]
            )
        else:
            relation_field_list.append(relation_field_dict)
