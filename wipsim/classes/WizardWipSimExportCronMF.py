from openerp import models, fields, api, _


class WizardWipSimExportCronMF(models.TransientModel):
    _name = "wizard.wipsim.export.cron.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    wipsim_export_mf = fields.Many2one("wipsim.export.mf", string="Area")
    active = fields.Boolean(string="Active")
    interval_number = fields.Integer(string="Interval Number", help="Repeat every x.")
    interval_type = fields.Selection([("minutes", "Minutes"), ("hours", "Hours"), ("work_days", "Work Days"),
                                      ("days", "Days"), ("weeks", "Weeks"), ("months", "Months")], "Interval Unit")
    nextcall = fields.Date(string="Next Execution Date", required=True, help="Next planned execution date for this job.")

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
            "active": self.active,
            "interval_number": self.interval_number,
            "interval_type": self.interval_type,
            "nextcall": self.nextcall,
            "model": "wipsim.export.mf",
            "function": "_export_work_orders_for_wipsim_export_mf",
            "args": repr([str(self.wipsim_export_mf.id)])
        })




