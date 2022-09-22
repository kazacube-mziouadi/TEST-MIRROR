from openerp import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def mf_create_simulation_by_quantity_button(self):
        return {
            "target": "current",
            "name": _("Simulation by quantity"),
            "type": "ir.actions.act_window",
            "res_model": "mf.simulation.by.quantity",
            "view_mode": "tree,form",
            "domain": [("mf_product_id","=",self.id)],
        }
        #    "view_mode": "form",
        #    "context": {
        #        "mf_product_id": self.id
        #    }
        #}
