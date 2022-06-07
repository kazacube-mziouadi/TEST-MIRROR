from openerp import models, fields, api, _, modules
from datetime import datetime
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
        config_default_end_time = mf_production_config_id.mf_default_end_time
        if not config_default_end_time:
            return fields.Datetime.now()
        today = datetime.today().strftime("%Y-%m-%d")
        default_end_time_hours_str = self.get_hours_str_from_time_float(config_default_end_time)
        default_end_time_minutes_str = self.get_minutes_str_from_time_float(config_default_end_time)
        company_timezone = pytz.timezone(self.env.user.company_id.tz)
        return company_timezone.fromutc(datetime.strptime(
            today + ' ' + default_end_time_hours_str + ':' + default_end_time_minutes_str, "%Y-%m-%d %H:%M"
        )).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_hours_str_from_time_float(time_float):
        default_end_time_integer_part_float = time_float // 1
        default_end_time_hours_int = int(default_end_time_integer_part_float)
        return str(default_end_time_hours_int)

    @staticmethod
    def get_minutes_str_from_time_float(time_float):
        default_end_time_decimal_part_float = time_float % 1
        default_end_time_minutes_int = int(round(60 * default_end_time_decimal_part_float))
        return str(default_end_time_minutes_int)
