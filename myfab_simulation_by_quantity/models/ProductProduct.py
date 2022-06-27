from openerp import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def mf_create_simulation_by_quantity_button(self):
        return {
            "name": _("Simulation by quantity"),
            "view_mode": "form",
            "res_model": "mf.simulation.by.quantity",
            "type": "ir.actions.act_window",
            "target": "current",
            "context": {
                "mf_product_id": self.id
            }
        }
