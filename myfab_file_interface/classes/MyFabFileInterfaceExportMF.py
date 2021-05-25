from openerp import models, fields, api, _
import json
import datetime
import os


class MyFabFileInterfaceExportMF(models.Model):
    _name = "myfab.file.interface.export.mf"
    _description = "MyFab file interface export configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=True, help='')
    files_path_mf = fields.Char(string="Files path", default="/etc/openprod_home/MyFabFileInterface/Exports/WorkOrders")
    planned_start_date_delta_min_mf = fields.Many2one("datetime.delta.mf", required=True,
                                                      string="Planned start date delta min")
    planned_start_date_delta_max_mf = fields.Many2one("datetime.delta.mf", required=True,
                                                      string="Planned start date delta max")
    areas_mf = fields.Many2many("mrp.area", "myfab_file_interface_export_mf_areas_rel",
                                "myfab_file_interface_export_id_mf", "area_id_mf", string="Areas", copy=False,
                                readonly=False)
    resources_mf = fields.Many2many("mrp.resource", "myfab_file_interface_export_mf_resources_rel",
                                    "myfab_file_interface_export_id_mf", "resource_id_mf", string="Resources",
                                    copy=False, readonly=False)
    last_json_generated_mf = fields.Text(string="Last JSON generated", readonly=True)
    cron_already_exists_mf = fields.Boolean(compute="_compute_cron_already_exists", readonly=True)
    number_of_work_orders_in_last_export = fields.Integer(string="Number of work orders in last export", readonly=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.one
    def _compute_cron_already_exists(self):
        existing_crons = self.env["ir.cron"].search([
            ("model", "=", "myfab.file.interface.export.mf"),
            ("function", "=", "export_work_orders"),
            ("args", "=", repr([self.id]))
        ], None, 1)
        if len(existing_crons) > 0:
            self.cron_already_exists_mf = True
        else:
            self.cron_already_exists_mf = False

    @api.one
    def export_work_orders(self):
        work_orders = self.get_work_orders_to_send_to_myfab_file_interface()
        self.number_of_work_orders_in_last_export = len(work_orders)
        json_content = self.format_work_orders_to_json_string(work_orders)
        self.write_myfab_file_interface_json_file(json_content)
        self.last_json_generated_mf = json_content

    def get_work_orders_to_send_to_myfab_file_interface(self):
        planned_start_date_min = self.planned_start_date_delta_min_mf.get_datetime_from_now()
        planned_start_date_max = self.planned_start_date_delta_max_mf.get_datetime_from_now()
        return self.env["mrp.workorder"].search([
            ('id', 'in', self.get_ids_of_work_orders_with_resources_or_areas_in_common())
            , ('planned_start_date', '>=', str(planned_start_date_min))
            , ('planned_start_date', '<=', str(planned_start_date_max))
        ])

    def get_ids_of_work_orders_with_resources_or_areas_in_common(self):
        all_work_orders = self.env["mrp.workorder"].search([])
        work_orders_with_resources_or_areas_in_common = []
        for work_order in all_work_orders:
            if (len(self.resources_mf) < 1 and self.areas_mf is None) \
                    or self.work_order_has_a_resource_and_an_area_in_common(work_order):
                work_orders_with_resources_or_areas_in_common.append(work_order.id)
        return work_orders_with_resources_or_areas_in_common

    def work_order_has_a_resource_and_an_area_in_common(self, work_order):
        for wo_resource in work_order.wo_resource_ids:
            if (len(self.resources_mf) < 1 or self.resource_is_in_self_resources(wo_resource.resource_id)) \
                    and (len(self.areas_mf) < 1 or self.work_order_has_a_an_area_in_common(work_order)):
                return True
        return False

    def resource_is_in_self_resources(self, resource):
        for selected_resource in self.resources_mf:
            if selected_resource.id == resource.id:
                return True
        return False

    def work_order_has_a_an_area_in_common(self, work_order):
        for wo_resource in work_order.wo_resource_ids:
            if self.area_is_in_self_areas(wo_resource.resource_id.area_id):
                return True
        return False

    def area_is_in_self_areas(self, area):
        for selected_area in self.areas_mf:
            if selected_area.id == area.id:
                return True
        return False

    @staticmethod
    def format_work_orders_to_json_string(work_orders):
        json_content = []
        for work_order in work_orders:
            json_content.append({
                "mrp.workorder": {
                    "name": work_order.name,
                    "display_name": work_order.display_name,
                    "final_product_id": {
                        "name": work_order.final_product_id.name,
                        "code": work_order.final_product_id.code
                    },
                    "rm_draft_ids": work_order.get_raw_materials_array(),
                    "state": work_order.state,
                    "requested_date": work_order.requested_date,
                    "min_date": work_order.min_date,
                    "max_date": work_order.max_date,
                    "planned_start_date": work_order.planned_start_date,
                    "planned_end_date": work_order.planned_end_date,
                    "real_start_date": work_order.real_start_date,
                    "real_end_date": work_order.real_end_date,
                    "mo_id": {
                        "name": work_order.mo_id.name
                    },
                    "sale_line_id": {
                        "display_name": work_order.sale_line_id.display_name
                    },
                    "affair_id": {
                        "name": work_order.affair_id.name
                    },
                    "sequence": work_order.sequence,
                    "produce_total_qty": work_order.produce_total_qty,
                    "quantity": work_order.quantity,
                    "uom_id": {
                        "name": work_order.uom_id.name
                    },
                    "availability": work_order.availability,
                    "advancement": work_order.advancement,
                    "percentage_overlap_next_ope": work_order.percentage_overlap_next_ope,
                    "customer_id": {
                        "name": work_order.customer_id.name
                    },
                    "wo_resource_ids": work_order.get_resources_array(),
                    "note_manufacturing": work_order.note_manufacturing
                }
            })
        return json.dumps(json_content, sort_keys=True, indent=4)

    def write_myfab_file_interface_json_file(self, json_content_string):
        now = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y%m%d_%H%M%S")
        if not os.path.exists(self.files_path_mf):
            os.makedirs(self.files_path_mf)
        file = open(os.path.join(self.files_path_mf, "MFFI-WorkOrders-" + now + ".json"), "a")
        file.write(json_content_string)
        file.close()

    @api.multi
    def generate_cron_for_export(self):
        return {
            'name': _("Generate cron for export"),
            'view_mode': 'form',
            'res_model': 'wizard.myfab.file.interface.export.cron.mf',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'myfab_file_interface_export_id': self.id}
        }

    @api.multi
    def delete_cron_for_export(self):
        self.env["ir.cron"].search([
            ("model", "=", "myfab.file.interface.export.mf"),
            ("function", "=", "export_work_orders"),
            ("args", "=", repr([self.id]))
        ], None, 1).unlink()
