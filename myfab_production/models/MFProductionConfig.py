from openerp import models, fields, api, _, modules
from openerp.exceptions import ValidationError


class MFProductionConfig(models.Model):
    _name = "mf.production.config"
    _description = "myfab production config"
    _sql_constraints = [
        (
            "name",
            "UNIQUE(name)",
            "There can only be one myfab production config"
        )
    ]

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", default=lambda self: self._get_default_name(), readonly=True)
    mf_use_default_end_time = fields.Boolean(
        string="Use default end time", default=False,
        help="Activate the use of the below default end time in the Create Timetracking wizard"
    )
    mf_default_end_time = fields.Float(string="Default end time", help="Format HH:MM")
    mf_default_end_time_timezone_name = fields.Char(string="Default end timezone name", store=True,
                                                    compute="_compute_mf_default_end_time_timezone_name")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @staticmethod
    def _get_default_name():
        return _("myfab production configuration")

    @api.one
    @api.constrains("mf_default_end_time")
    def _check_mf_default_end_time(self):
        if self.mf_default_end_time >= 24:
            raise ValidationError(_("The time tracking's default end time can not be greater than 23:59"))

    @api.one
    @api.depends("mf_default_end_time")
    def _compute_mf_default_end_time_timezone_name(self):
        self.mf_default_end_time_timezone_name = self.env.user.company_id.tz
