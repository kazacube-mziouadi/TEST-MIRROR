from openerp import models, fields, api, _
import json
from datetime import datetime

class WipSimExportMF(models.Model):
    _name = "wipsim.export.mf"
    _description = "WipSim export configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=True, help='')
    date_min = fields.Date(string='Minimum date', required=True)
    date_max = fields.Date(string='Maximum date', required=True)
    resources = fields.Many2many('mrp.resource', 'wipsim_export_mf_resources_rel', 'wipsim_export_id', 'resource_id',
                                 string='Resources', copy=False, readonly=False)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.multi
    def button_export_work_orders(self):
        print("EXPORTING")
        work_orders = self.env["mrp.workorder"].search([
            ('requested_date', '>=', self.date_min)
            , ('requested_date', '<=', self.date_max)
            # ,('first_resource_id', 'in', [self.resources])
        ])
        json_content = []
        for work_order in work_orders:
            json_content.append({
                "name": work_order.name,
                "requested_date": work_order.requested_date,
                "final_product": work_order.final_product_id.name,
                "customer": work_order.customer_id.name,
            })
        print(json.dumps(json_content))
        now = datetime.now().strftime("%d%m%Y_%H%M%S")
        file = open("/etc/openprod_home/WipSim/OTs/WipSim-WorkOrders-" + now + ".json", "a")
        file.write(json.dumps(json_content))
        file.close()
