from openerp import models, fields, api, _


class quotation(models.Model):
    _inherit = "quotation"

    @api.multi
    def mf_create_simulation_by_quantity_button(self):
        type_of_screen = {
            "target": "current",
            "name": _("Simulation by quantity"),
            "type": "ir.actions.act_window",
            "res_model": "mf.simulation.by.quantity",
            "domain": [("mf_quotation_id","=",self.id)],
            "context": {
                "mf_quotation_id": self.id,
            },
        }

        if self.env["mf.simulation.by.quantity"].search([("mf_quotation_id","=",self.id)]):
            type_of_screen["view_mode"] = "tree,form"
        else:
            type_of_screen["view_mode"] = "form"

        return type_of_screen
