# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, modules
from datetime import datetime
import pytz

class MFTools(models.Model):
    _name = "mf.tools"

    ####################################################################
    # DATE & TIME conversion tools
    ####################################################################
    def mf_convert_from_tz_to_UTC(self, date_in, t_from, date_in_format = '%Y-%m-%d %H:%M:%S'):
        return self.mf_convert_tz(date_in, t_from, 'UTC', date_in_format)

    def mf_convert_from_UTC_to_tz(self, date_in, t_to, date_in_format = '%Y-%m-%d %H:%M:%S'):
        return self.mf_convert_tz(date_in, 'UTC', t_to, date_in_format)

    def mf_get_time_str_from_time_float(self, time_float):
        return self.mf_get_hours_str_from_time_float(time_float) + ':' + self.mf_get_minutes_str_from_time_float(time_float)

    @staticmethod
    def mf_convert_tz(date_in, t_from, t_to, date_in_format ='%Y-%m-%d %H:%M:%S'):
        date_in = datetime.strptime(date_in, date_in_format)
        tz_from = pytz.timezone(t_from)
        date_without_tz = tz_from.localize(date_in)
        tz_to = pytz.timezone(t_to)
        date_out = date_without_tz.astimezone(tz_to)
        return (date_out)

    @staticmethod
    def mf_get_hours_str_from_time_float(time_float):
        # Get integer part of float
        default_end_time_integer_part_float = time_float // 1
        return str(int(default_end_time_integer_part_float))

    @staticmethod
    def mf_get_minutes_str_from_time_float(time_float):
        # Get decimal part of float
        default_end_time_decimal_part_float = time_float % 1
        return str(int(round(60 * default_end_time_decimal_part_float)))

    ####################################################################
    # Dynamic execution tools
    ####################################################################
    """
       Launch a method at string format (for example) "method_name(paramInt, 'paramString')" on a list of records.
       It's not a static method as "self" is used through the exec() method
    """
    def mf_launch_method_on_records(self, method_name, record_ids):
        record_ids_str_ids_list = [str(record_id.id) for record_id in record_ids]
        if method_name[-1:] != ')':
            method_name += "()"
        exec("self.env['" + record_ids[0]._name + "'].search([('id', 'in', " + str(record_ids_str_ids_list) + ")])." + method_name)

    ####################################################################
    # Fields tools
    ####################################################################
    """
        For a given many2one ir.model.field, returns the reverse field one2many field
    """
    def mf_get_reverse_field_id(self, field_id):
        model_id = self.env["ir.model"].search([("model", '=', field_id.relation)])
        if field_id.relation_field:
            # relation_field is only the string name of the reverse relation field ; we have to return the field record
            return self.env["ir.model.fields"].search([("model_id", '=', model_id.id), ("name", '=', field_id.relation_field)])
        else:
            return self.env["ir.model.fields"].search([
                ("model_id", '=', model_id.id), ("relation", '=', field_id.model_id.model), ("relation_field", '=', field_id.name)
            ])

    ####################################################################
    # Comparison tools
    ####################################################################
    """
        Compare 2 lists : return True if equals, else False
    """
    @staticmethod
    def are_lists_equal(list1, list2):
        list1.sort()
        list2.sort()
        return list1 == list2

    """
        Compare 2 values, with the second one casted to the type of the first.
        Return True if equals, else False.
    """
    def are_values_equal_in_same_type(self, value_with_master_type, value_to_compare_with):
        if (value_to_compare_with and self.is_value_empty(value_with_master_type)) or (
            value_with_master_type and self.is_value_empty(value_to_compare_with)
        ):
            return False
        return value_with_master_type == type(value_with_master_type)(value_to_compare_with)

    @staticmethod
    def is_value_empty(value):
        return value is False or value is None or (hasattr(value, "_name") and not value)

    """
        Compare a dict of field values and a record. If the dict has the same values than the record, return True.
        Else return False.
    """
    def are_dict_and_record_values_equals(self, values_dict, record_id):
        for field_name in values_dict.keys():
            field_value = values_dict[field_name]
            if type(field_value) in [list, dict, tuple]:
                continue
            record_field_value = getattr(record_id, field_name)
            if hasattr(record_field_value, "id"):
                record_field_value = record_field_value.id
            if not self.are_values_equal_in_same_type(record_field_value, values_dict[field_name]):
                return False
        return True

    ####################################################################
    # Dict tools
    ####################################################################
    @staticmethod
    def merge_two_dicts(dict_1, dict_2):
        merged_dict = dict_1.copy()   # copies keys and values of x
        merged_dict.update(dict_2)    # modifies z with keys and values of y
        return merged_dict

    ####################################################################
    # ORM tools
    ####################################################################
    def write_different_fields_only(self, record_id, fields_dict):
        different_fields_dict = {}
        print("*/*/*/*/*//--*-/")
        print(record_id)
        for field_name in fields_dict.keys():
            update_field_value = fields_dict[field_name]
            field_id = self.env["ir.model.fields"].search(
                [("model_id", "=", record_id._name), ("name", "=", field_name)]
            )
            record_field_value = getattr(record_id, field_name)
            if field_id.ttype == "many2one" and record_field_value:
                record_field_value = record_field_value.id
            if field_id.ttype in ["one2many", "many2many"]:
                print("**O2M***")
                print(update_field_value)
                update_field_value_ids_list = [update_tuple[1] for update_tuple in update_field_value]
                record_field_value_ids_list = record_field_value.ids
                if not self.are_lists_equal(update_field_value_ids_list, record_field_value_ids_list):
                    relation_field_values_to_add_list = []
                    for update_tuple in update_field_value:
                        if update_tuple[1] not in record_field_value_ids_list:
                            relation_field_values_to_add_list.append(update_tuple)
                    different_fields_dict[field_name] = relation_field_values_to_add_list
                    print("**ADDING***")
                    print(different_fields_dict)
            elif not self.are_values_equal_in_same_type(record_field_value, update_field_value):
                # print("***///****")
                # print(record_field_value)
                # print(update_field_value)
                different_fields_dict[field_name] = update_field_value
        if different_fields_dict:
            print("***WRITE***")
            print(record_id)
            print(different_fields_dict)
            record_id.write(different_fields_dict)
            return different_fields_dict
        return False