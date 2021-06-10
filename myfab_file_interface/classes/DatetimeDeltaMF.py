from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import datetime


class DatetimeDeltaMF(models.Model):
    _name = "datetime.delta.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=False, help='')
    delta_number_mf = fields.Integer(string="Delta Number", required=True)
    delta_type_mf = fields.Selection([
        ("minutes", "Minutes"), ("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks")
    ], "Delta Unit", required=True)
    delta_orientation_mf = fields.Selection([
        ("-", "Before now"), ("+", "After now")
    ], "Delta Orientation", required=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.model
    def create(self, fields_list):
        fields_list["name"] = fields_list["delta_orientation_mf"] + " " + str(fields_list["delta_number_mf"]) \
                              + " " + _(fields_list["delta_type_mf"])
        return super(DatetimeDeltaMF, self).create(fields_list)

    def get_datetime_from_now(self):
        now = datetime.datetime.now() + datetime.timedelta(hours=2)
        time_delta = str("datetime.timedelta(" + self.delta_type_mf + "=" + str(self.delta_number_mf) + ")")
        if self.delta_orientation_mf == "+":
            return now + eval(time_delta)
        elif self.delta_orientation_mf == "-":
            return now - eval(time_delta)
        raise ValidationError('The operator must be + or -')
