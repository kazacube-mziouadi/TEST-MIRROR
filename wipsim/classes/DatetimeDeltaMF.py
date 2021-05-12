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

    @api.model
    def create(self, fields_list):
        print("#################")
        print(_(fields_list["delta_type_mf"]))
        print(fields_list["delta_type_mf"])
        fields_list["name"] = fields_list["delta_orientation_mf"] + " " + str(fields_list["delta_number_mf"]) \
                              + " " + _(fields_list["delta_type_mf"])
        return super(DatetimeDeltaMF, self).create(fields_list)

    def get_datetime_from_now(self):
        now = datetime.datetime.now() + datetime.timedelta(hours=2)
        time_delta = "datetime.timedelta(" + self.delta_type_mf + "=" + str(self.delta_number_mf) + ")"
        print("TO EVAL *************")
        print(now + self.delta_orientation_mf + time_delta())
        return eval(now + self.delta_orientation_mf + time_delta())
