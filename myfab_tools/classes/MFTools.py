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
       Launch a method at format (for example) "method_name(paramInt, 'paramString')" on a list of records.
       It's not a static method as "self" is used through the exec() method
    """
    def mf_launch_method_on_records(self, method_name, record_ids):
        record_ids_str_ids_list = [str(record_id.id) for record_id in record_ids]
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
    @staticmethod
    def are_values_equal_in_same_type(value_with_master_type, value_to_compare_with):
        if (value_to_compare_with and (value_with_master_type is False or value_with_master_type is None)) or (
            value_with_master_type and (value_to_compare_with is False or value_to_compare_with is None)
        ):
            return False
        return value_with_master_type == type(value_with_master_type)(value_to_compare_with)
