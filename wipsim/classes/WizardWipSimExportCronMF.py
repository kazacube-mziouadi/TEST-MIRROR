from openerp import models, fields, api, _


class WizardWipSimExportCronMF(models.TransientModel):
    _name = "wizard.wipsim.export.cron.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=32, required=False)
    wipsim_export_mf = fields.Many2one("wipsim.export.mf", string="Area")
    where_mf = fields.Char(string="Where", size=128, required=False)
    who_mf = fields.Char(string="Who", size=128, required=False)

    @api.model
    def default_get(self, fields_list):
        res = super(WizardWipSimExportCronMF, self).default_get(fields_list=fields_list)
        res["wipsim_export_mf"] = self.env.context.get('wipsim_export_id')
        return res

    @api.multi
    def action_validate(self):
        pass




