from openerp import models, fields, api, _
import json
import datetime
import os


class WipSimExportMF(models.Model):
    _name = "wipsim.export.mf"
    _description = "WipSim export configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=True, help='')
    files_path_mf = fields.Char(string="Files path", default="/etc/openprod_home/WipSim/OTs")
    date_min_mf = fields.Date(string="Minimum date", required=True)
    date_max_mf = fields.Date(string="Maximum date", required=True)
    resources_mf = fields.Many2many("mrp.resource", "wipsim_export_mf_resources_rel", "wipsim_export_id_mf",
                                    "resource_id_mf", string="Resources", copy=False, readonly=False)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.multi
    def button_export_work_orders(self):
        print("EXPORTING")
        work_orders = self.get_work_orders_to_send_to_wipsim()
        json_content = self.format_work_orders_to_json(work_orders)
        print(json.dumps(json_content))
        self.write_wipsim_json_file(json_content)

    def get_work_orders_to_send_to_wipsim(self):
        return self.env["mrp.workorder"].search([
            ('id', 'in', self.get_work_orders_with_resources_in_common())
            , ('requested_date', '>=', self.date_min_mf)
            , ('requested_date', '<=', self.date_max_mf)
        ])

    def get_work_orders_with_resources_in_common(self):
        all_work_orders = self.env["mrp.workorder"].search([])
        work_orders_with_resources_in_common = []
        for work_order in all_work_orders:
            if self.work_order_has_a_resource_in_common(work_order):
                work_orders_with_resources_in_common.append(work_order.id)
        return work_orders_with_resources_in_common

    def work_order_has_a_resource_in_common(self, work_order):
        for wo_resource in work_order.wo_resource_ids:
            for resource in self.resources_mf:
                if resource.id == wo_resource.resource_id.id:
                    return True
        return False

    @staticmethod
    def format_work_orders_to_json(work_orders):
        json_content = []
        for work_order in work_orders:
            json_content.append({
                "name": work_order.name,
                "requested_date": work_order.requested_date,
                "final_product": work_order.final_product_id.name,
                "customer": work_order.customer_id.name,
                "resources": work_order.get_resources_names_array()
            })
        return json_content

    def write_wipsim_json_file(self, json_content):
        now = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%d%m%Y_%H%M%S")
        if not os.path.exists(self.files_path_mf):
            os.makedirs(self.files_path_mf)
        file = open(os.path.join(self.files_path_mf, "WipSim-WorkOrders-" + now + ".json"), "a")
        file.write(json.dumps(json_content))
        file.close()
