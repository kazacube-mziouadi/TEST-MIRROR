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
    name = fields.Char(string="Name", default=_("myfab production configuration"), readonly=True)
    mf_default_end_time = fields.Float(string="Default end time", help="Format HH:MM")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.one
    @api.constrains("mf_default_end_time")
    def _check_mf_default_end_time(self):
        if self.mf_default_end_time >= 24:
            raise ValidationError(_("The time tracking's default end time can not be greater than 23:59"))
