from openerp import models, fields, api, _


class WizardMyFabFileInterfaceExportCronMF(models.TransientModel):
    _name = "wizard.myfab.file.interface.export.cron.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False, default="default")
    myfab_file_interface_export_mf = fields.Many2one("myfab.file.interface.export.mf", string="Area")
    interval_number = fields.Integer(string="Interval Number", help="Repeat every x.", required=True)
    interval_type = fields.Selection([
        ("minutes", "Minutes"), ("hours", "Hours"), ("work_days", "Work Days"),
        ("days", "Days"), ("weeks", "Weeks"), ("months", "Months")
    ], "Interval Unit", required=True)
    nextcall = fields.Datetime(string="Next Execution Date", required=True,
                               help="Next planned execution date for this job.")

    @api.model
    def default_get(self, fields_list):
        res = super(WizardMyFabFileInterfaceExportCronMF, self).default_get(fields_list=fields_list)
        res["myfab_file_interface_export_mf"] = self.env.context.get("myfab_file_interface_export_id")
        return res

    @api.multi
    def action_validate(self):
        self.env["ir.cron"].create({
            "name": "MyFab File Interface Export Cron - " + self.myfab_file_interface_export_mf.name
                    + " [" + str(self.myfab_file_interface_export_mf.id) + "]",
            "user_id": self.env.user.id,
            "active": True,
            "interval_number": self.interval_number,
            "interval_type": self.interval_type,
            "nextcall": self.nextcall,
            "numbercall": -1,
            "model": "myfab.file.interface.export.mf",
            "function": "export_work_orders",
            "args": repr([self.myfab_file_interface_export_mf.id])
        })




