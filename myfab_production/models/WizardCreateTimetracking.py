from openerp import models, fields, api, _, modules
from datetime import datetime, date, timedelta


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
        end_datetime_at_user_timezone = datetime.strptime(
            today_str + ' ' + self.env['tools.mf'].mf_get_time_str_from_time_float(config_default_end_time), "%Y-%m-%d %H:%M"
        )
        # TODO : In Odoo, the timezone for datetime display is taken from the browser timezone.
        #  So if the user's timezone is != from it's browser timezone, the end_datetime default setting will not be ok
        end_datetime_utc = self.env['tools.mf'].mf_convert_from_tz_to_UTC(str(end_datetime_at_user_timezone), self.env.user.tz)
        return end_datetime_utc.strftime("%Y-%m-%d %H:%M:%S")