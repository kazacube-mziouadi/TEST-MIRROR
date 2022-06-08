from openerp import models, fields, api, _, modules
from datetime import datetime, timedelta
import pytz


class WizardCreateTimetracking(models.Model):
    _inherit = "wizard.create.timetracking"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    end_date = fields.Datetime(default=lambda self: self._get_default_datetime())

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def _get_default_datetime(self):
        mf_production_config_id = self.env["mf.production.config"].search([], None, 1)
        use_config_default_end_time = mf_production_config_id.mf_use_default_end_time
        config_default_end_time = mf_production_config_id.mf_default_end_time
        config_default_end_time_timezone_name = mf_production_config_id.mf_default_end_time_timezone_name
        if not use_config_default_end_time:
            return fields.Datetime.now()
        config_default_end_time_timezone_offset_int = self.get_timezone_offset_int(config_default_end_time_timezone_name)
        today_str = datetime.today().strftime("%Y-%m-%d")
        end_time_hours_str = self.get_hours_str_from_time_float(config_default_end_time)
        end_time_minutes_str = self.get_minutes_str_from_time_float(config_default_end_time)
        end_datetime_utc0 = datetime.strptime(
            today_str + ' ' + end_time_hours_str + ':' + end_time_minutes_str, "%Y-%m-%d %H:%M"
        )
        end_datetime_correct_utc = end_datetime_utc0 - timedelta(hours=config_default_end_time_timezone_offset_int)
        return end_datetime_correct_utc.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_hours_str_from_time_float(time_float):
        # Get integer part of float
        default_end_time_integer_part_float = time_float // 1
        default_end_time_hours_int = int(default_end_time_integer_part_float)
        return str(default_end_time_hours_int)

    @staticmethod
    def get_minutes_str_from_time_float(time_float):
        # Get decimal part of float
        default_end_time_decimal_part_float = time_float % 1
        default_end_time_minutes_int = int(round(60 * default_end_time_decimal_part_float))
        return str(default_end_time_minutes_int)

    # Returns the timezone offset as an int
    @staticmethod
    def get_timezone_offset_int(timezone):
        # The offset at format +01:00 or -02:00 for example
        offset_str = str(datetime.now(pytz.timezone(timezone)))[-6:]
        operator_str = offset_str[0]
        offset_hours_int = int(offset_str[1:3])
        if operator_str == '+':
            return offset_hours_int
        else:
            return -offset_hours_int
