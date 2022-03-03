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
        # TODO : on ne doit pas pouvoir choisir du TXT = on le traitera soit comme du JSON soit comme du CSV
        return self.get_records_from_csv(file_content, file_name, "\t", file_quoting, file_encoding)

    def get_records_from_csv(self, file_content, file_name, file_separator, file_quoting, file_encoding):
        model_name = self.env["file.mf"].get_model_name_from_file_name(file_name)
        csv_rows = csv.reader(
            StringIO(file_content), delimiter=str(file_separator),
            quotechar=str(file_quoting) if file_quoting else None
        )
        records_list = []
        # list containing the corresponding ir.model.field of each field, and a dict tree for relation fields
        # [{'field': ir.model.fields(13606,)}, {'field': ir.model.fields(2050,), 'sub_field': {'field': ...}}]
        fields_list = []
        # dict containing the index of the relation field to process for each depth of a root record
        # {depth: index, depth: index, ...}
        index_to_process_for_depth_dict = {}
        for csv_row_index, csv_row in enumerate(csv_rows):
            csv_row = [cell.decode(file_encoding) for cell in csv_row]
            if csv_row_index == 0:
                field_names_list = csv_row
                fields_list = self.get_fields_by_names_list(field_names_list, model_name)
            else:
                # TODO : COMMENTAIRES !
                record_values_dict, is_root_record, record_to_write_id = self.get_record_dict_from_values_list(
                    csv_row, fields_list
                )
                if is_root_record:
                    index_to_process_for_depth_dict = {}
                    record_to_append = {
                        "method": "write" if record_to_write_id else "create",
                        "model": model_name,
                        "fields": {"id": record_to_write_id} if record_to_write_id else record_values_dict,
                        "rows": [csv_row]
                    }
                    if record_to_write_id:
                        record_to_append["write"] = record_values_dict
                    records_list.append(record_to_append)
                else:
                    # TODO : COMMENTAIRES !
                    last_relation_field_processed_depth = self.add_relation_field_dict_to_relation_field_list(
                        record_values_dict,
                        [records_list[-1]["fields"]],
                        index_to_process_for_depth_dict
                    )
                    records_list[-1]["rows"].append(csv_row)
                    index_to_process_for_depth_dict[last_relation_field_processed_depth] += 1
        return records_list

    def get_fields_by_names_list(self, field_names_list, model_name):
        fields_list = []
        for field_name in field_names_list:
            fields_list.append(self.get_field_by_name_tree(field_name, model_name))
        return fields_list

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
                    if field.name == "id" and values_list[field_index].isdecimal():
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
