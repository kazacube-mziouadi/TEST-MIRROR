from openerp import models, fields, api, _
import datetime


class DatetimeDeltaMF(models.Model):
    _name = "datetime.delta.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=False, help='')
    delta_number_mf = fields.Integer(string="Delta Number", help="Repeat every x.", required=True)
    delta_type_mf = fields.Selection([
        ("minutes", "Minutes"), ("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks"), ("months", "Months")
    ], "Delta Unit", required=True)
    delta_orientation_mf = fields.Selection([
        ("-", "Before now"), ("+", "After now")
    ], "Delta Orientation", required=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def get_datetime_from_now(self):
        now = datetime.datetime.now() + datetime.timedelta(hours=2)
        time_delta = "datetime.timedelta(" + self.delta_type_mf + "=" + self.delta_number_mf + ")"
        return eval(now + self.delta_orientation_mf + time_delta())
