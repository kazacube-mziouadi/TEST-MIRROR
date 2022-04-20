from openerp import models, fields, api, _


class WizardFileInterfaceCronMF(models.TransientModel):
    _name = "wizard.file.interface.cron.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False, default="default")
    interval_number_mf = fields.Integer(string="Interval Number", help="Repeat every x.", required=True)
    interval_type_mf = fields.Selection([
        ("minutes", "Minutes"), ("hours", "Hours"), ("work_days", "Work Days"),
        ("days", "Days"), ("weeks", "Weeks"), ("months", "Months")
    ], "Interval Unit", required=True)
    nextcall_mf = fields.Datetime(string="Next Execution Date", required=True,
                                  help="Next planned execution date for this job.")
    record_model_name_mf = fields.Char(string="Model of record on which apply cron", required=True)
    record_name_mf = fields.Char(string="Name of record on which apply cron", required=True)
    record_id_mf = fields.Integer(string="ID of record on which apply cron", required=True)
    record_method_mf = fields.Char(string="Method to execute on model", required=True)

    @api.model
    def default_get(self, fields_list):
        res = super(WizardFileInterfaceCronMF, self).default_get(fields_list=fields_list)
        res["record_model_name_mf"] = self.env.context.get("record_model_name_mf")
        res["record_name_mf"] = self.env.context.get("record_name_mf")
        res["record_id_mf"] = self.env.context.get("record_id_mf")
        res["record_method_mf"] = self.env.context.get("record_method_mf")
        return res

    @api.multi
    def action_validate(self):
        self.env["ir.cron"].create({
            "name": "myfab File Interface Cron - " + self.record_name_mf
                    + " [" + str(self.record_id_mf) + "]",
            "user_id": self.env.user.id,
            "active": True,
            "interval_number": self.interval_number_mf,
            "interval_type": self.interval_type_mf,
            "nextcall": self.nextcall_mf,
            "numbercall": -1,
            "model": self.record_model_name_mf,
            "function": self.record_method_mf,
            "args": repr([self.record_id_mf])
        })




