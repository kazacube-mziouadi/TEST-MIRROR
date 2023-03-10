from openerp import models, fields, api, _


class WizardMyFabFileInterfaceCronMF(models.TransientModel):
    _name = "wizard.myfab.file.interface.cron.mf"

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
    object_model_name_mf = fields.Char(string="Model of object on which apply cron", size=64, required=True)
    object_name_mf = fields.Char(string="Name of object on which apply cron", size=64, required=True)
    object_id_mf = fields.Integer(string="ID of object on which apply cron", size=64, required=True)
    object_method_mf = fields.Char(string="Method to execute on model", size=64, required=True)

    @api.model
    def default_get(self, fields_list):
        res = super(WizardMyFabFileInterfaceCronMF, self).default_get(fields_list=fields_list)
        res["object_model_name_mf"] = self.env.context.get("object_model_name_mf")
        res["object_name_mf"] = self.env.context.get("object_name_mf")
        res["object_id_mf"] = self.env.context.get("object_id_mf")
        res["object_method_mf"] = self.env.context.get("object_method_mf")
        return res

    @api.multi
    def action_validate(self):
        self.env["ir.cron"].create({
            "name": "MyFab File Interface Cron - " + self.object_name_mf
                    + " [" + str(self.object_id_mf) + "]",
            "user_id": self.env.user.id,
            "active": True,
            "interval_number": self.interval_number_mf,
            "interval_type": self.interval_type_mf,
            "nextcall": self.nextcall_mf,
            "numbercall": -1,
            "model": self.object_model_name_mf,
            "function": self.object_method_mf,
            "args": repr([self.object_id_mf])
        })




