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
    mf_planned_ressource = fields.Boolean(string="Activate Planned ressource management",default=False)
    mf_default_end_time = fields.Float(string="Default end time", help="Format HH:MM")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @staticmethod
    def _get_default_name():
        return "myfab production configuration"

    @api.one
    @api.constrains("mf_default_end_time")
    def _check_mf_default_end_time(self):
        if self.mf_default_end_time >= 24:
            raise ValidationError(_("The time tracking's default end time can not be greater than 23:59"))
    
    @api.multi
    def write(self, vals):
        if 'mf_planned_ressource' in vals:
            if vals['mf_planned_ressource'] == True:
                users = self.env['res.users'].search([])
                data_xml = self.env['ir.model.data'].search([("name","=","group_menu_planned_ressource")])
                group = self.env['res.groups'].browse(data_xml.res_id)
                group.write({"users":[(6, 0, users.ids)]})
            else:
                data_xml = self.env['ir.model.data'].search([("name","=","group_menu_planned_ressource")])
                group = self.env['res.groups'].browse(data_xml.res_id)
                group.write({"users":[(5, 0, 0)]})
        return super(MFProductionConfig, self).write(vals)



