from openerp import models, fields, api, _


class WizardWipSimExportCronMF(models.TransientModel):
    _name = "wizard.wipsim.export.cron.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    wipsim_export_mf = fields.Many2one("wipsim.export.mf", string="Area")
    interval_number = fields.Integer(string="Interval Number", help="Repeat every x.", required=True)
    interval_type = fields.Selection([
            ("minutes", "Minutes"), ("hours", "Hours"), ("work_days", "Work Days"),
            ("days", "Days"), ("weeks", "Weeks"), ("months", "Months")
        ], "Interval Unit", required=True)
    nextcall = fields.Datetime(string="Next Execution Date", required=True, help="Next planned execution date for this job.")

    @api.model
    def default_get(self, fields_list):
        res = super(WizardWipSimExportCronMF, self).default_get(fields_list=fields_list)
        res["wipsim_export_mf"] = self.env.context.get("wipsim_export_id")
        return res

    @api.multi
    def action_validate(self):
        self.env["ir.cron"].create({
            "name": "WipSim Export Cron - " + self.wipsim_export_mf.name + " [" + str(self.wipsim_export_mf.id) + "]",
            "user_id": self.env.user.id,
            "active": True,
            "interval_number": self.interval_number,
            "interval_type": self.interval_type,
            "nextcall": self.nextcall,
            "numbercall": -1,
            "model": "wipsim.export.mf",
            "function": "export_work_orders",
            "args": repr([self.wipsim_export_mf.id])
        })




