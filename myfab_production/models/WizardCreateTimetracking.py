from openerp import models, fields, api, _, modules
from datetime import datetime, timedelta
import pytz


class WizardCreateTimetracking(models.Model):
    _inherit = "wizard.create.timetracking"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    end_date = fields.Datetime(default=lambda self: self._mf_get_default_end_date())

    # ===========================================================================
    # METHODS
    # ===========================================================================
    def _mf_get_default_end_date(self):
        mf_production_config_id = self.env["mf.production.config"].search([], None, 1)
        if not mf_production_config_id.mf_use_default_end_time:
            return fields.Datetime.now()
        config_default_end_time = mf_production_config_id.mf_default_end_time
        today_str = datetime.today().strftime("%Y-%m-%d")
        end_time_hours_str = self.get_hours_str_from_time_float(config_default_end_time)
        end_time_minutes_str = self.get_minutes_str_from_time_float(config_default_end_time)
        end_datetime_at_user_timezone = datetime.strptime(
            today_str + ' ' + end_time_hours_str + ':' + end_time_minutes_str, "%Y-%m-%d %H:%M"
        )
        # TODO : In Odoo, the timezone for datetime display is taken from the browser timezone.
        #  So if the user's timezone is != from it's browser timezone, the end_datetime default setting will not be ok
        end_datetime_utc = self.convert_tz(str(end_datetime_at_user_timezone), self.env.user.tz, "UTC")
        return end_datetime_utc.strftime("%Y-%m-%d %H:%M:%S")

    # TODO : Planify to add this method to a class installed with the myfab base package
    @staticmethod
    def convert_tz(date, t_from, t_to):
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        tz = pytz.timezone(t_from)
        date_user = tz.localize(date)
        tz1 = pytz.timezone(t_to)
        return date_user.astimezone(tz1)

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
