# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, modules
from openerp.exceptions import ValidationError
from datetime import datetime, date, timedelta
import pytz

class ToolsMF(models.Model):
    _name = "tools.mf"

    ####################################################################
    # DATE & TIME conversion tools
    ####################################################################
    def mf_convert_from_tz_to_UTC(self, date_in, t_from, date_in_format = '%Y-%m-%d %H:%M:%S'):
        return self.mf_convert_tz(date_in, t_from, 'UTC', date_in_format)

    def mf_convert_from_UTC_to_tz(self, date_in, t_to, date_in_format = '%Y-%m-%d %H:%M:%S'):
        return self.mf_convert_tz(date_in, 'UTC', t_to, date_in_format)

    def mf_get_time_str_from_time_float(self, time_float):
        return self.mf_get_hours_str_from_time_float(time_float) + ':' + self.mf_get_minutes_str_from_time_float(time_float)


    def mf_convert_tz(self, date_in, t_from, t_to, date_in_format = '%Y-%m-%d %H:%M:%S'):
        date_in = datetime.strptime(date_in, date_in_format)
        tz_from = pytz.timezone(t_from)
        date_without_tz = tz_from.localize(date_in)
        tz_to = pytz.timezone(t_to)
        date_out = date_without_tz.astimezone(tz_to)
        return (date_out)

    def mf_get_hours_str_from_time_float(self, time_float):
        # Get integer part of float
        default_end_time_integer_part_float = time_float // 1
        return str(int(default_end_time_integer_part_float))

    def mf_get_minutes_str_from_time_float(self,  time_float):
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

