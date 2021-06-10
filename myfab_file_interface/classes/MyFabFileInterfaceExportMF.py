from openerp import models, fields, api, _
import json
import datetime
import os
import base64


class MyFabFileInterfaceExportMF(models.Model):
    _name = "myfab.file.interface.export.mf"
    _description = "MyFab file interface export configuration"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, required=True, help='')
    import_directory_path_mf = fields.Char(string="Files path",
                                           default="/etc/openprod_home/MyFabFileInterface/Exports/WorkOrders")
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
    models_to_export_mf = fields.Many2many("model.export.mf", "myfab_file_interface_export_mf_model_export_mf_rel",
                                           "myfab_file_interface_export_mf_id", "model_export_mf_id",
                                           string="Models to export", copy=False, readonly=False)
    last_json_generated_mf = fields.Text(string="Last JSON generated", readonly=True)
    last_json_generated_name_mf = fields.Char(string="Last JSON generated name", readonly=True)
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
        json_content = {
            "mrp.manufacturingorders": {}
        }
        for work_order in work_orders:
            manufacturing_order = work_order.mo_id
            manufacturing_order_dict = {
                "affair_id": {
                    "name": manufacturing_order.affair_id.name
                },
                "customer_id": {
                    "name": manufacturing_order.customer_id.name
                },
                "display_name": manufacturing_order.display_name,
                "min_start_date": manufacturing_order.min_start_date,
                "max_end_date": manufacturing_order.max_end_date,
                "name": manufacturing_order.name,
                "needed_quantity": manufacturing_order.needed_quantity,
                "planned_start_date": manufacturing_order.planned_start_date,
                "planned_end_date": manufacturing_order.planned_end_date,
                "product_id": {
                    "name": manufacturing_order.product_id.name,
                    "code": manufacturing_order.product_id.code,
                    "track_label": manufacturing_order.product_id.track_label
                },
                "quantity": manufacturing_order.quantity,
                "requested_date": manufacturing_order.requested_date,
                "routing_id": {
                    "name": manufacturing_order.routing_id.name
                },
                "sale_line_id": {
                    "display_name": manufacturing_order.sale_line_id.display_name
                },
                "uom_id": {
                    "name": manufacturing_order.uom_id.name
                }
            }
            work_orders_for_manufacturing_order = {}
            for work_order_not_sorted_yet in work_orders:
                if work_order_not_sorted_yet.mo_id.id == manufacturing_order.id:
                    work_orders_for_manufacturing_order[work_order_not_sorted_yet.display_name] = {
                        "advancement": work_order_not_sorted_yet.advancement,
                        "availability": work_order_not_sorted_yet.availability,
                        "display_name": work_order_not_sorted_yet.display_name,
                        "fp_draft_ids": work_order_not_sorted_yet.get_final_products_array(),
                        "min_date": work_order_not_sorted_yet.min_date,
                        "max_date": work_order_not_sorted_yet.max_date,
                        "name": work_order_not_sorted_yet.name,
                        "note_manufacturing": work_order_not_sorted_yet.note_manufacturing,
                        "percentage_overlap_next_ope": work_order_not_sorted_yet.percentage_overlap_next_ope,
                        "planned_start_date": work_order_not_sorted_yet.planned_start_date,
                        "planned_end_date": work_order_not_sorted_yet.planned_end_date,
                        "produce_total_qty": work_order_not_sorted_yet.produce_total_qty,
                        "real_start_date": work_order_not_sorted_yet.real_start_date,
                        "real_end_date": work_order_not_sorted_yet.real_end_date,
                        "requested_date": work_order_not_sorted_yet.requested_date,
                        "rm_draft_ids": work_order_not_sorted_yet.get_raw_materials_array(),
                        "quantity": work_order_not_sorted_yet.quantity,
                        "sequence": work_order_not_sorted_yet.sequence,
                        "state": work_order_not_sorted_yet.state,
                        "uom_id": {
                            "name": work_order_not_sorted_yet.uom_id.name
                        },
                        "wo_resource_ids": work_order_not_sorted_yet.get_resources_array()
                    }
            manufacturing_order_dict["workorder_ids"] = work_orders_for_manufacturing_order
            json_content["mrp.manufacturingorders"][manufacturing_order.display_name] = manufacturing_order_dict
        return json.dumps(json_content, sort_keys=True, indent=4)

    def write_myfab_file_interface_json_file(self, json_content_string):
        now = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y%m%d_%H%M%S")
        if not os.path.exists(self.import_directory_path_mf):
            os.makedirs(self.import_directory_path_mf)
        file_name = "MFFI-WorkOrders-" + now + ".json"
        file_path = os.path.join(self.import_directory_path_mf, file_name)
        file = open(file_path, "a")
        file.write(json_content_string)
        file.close()
        self.last_json_generated_name_mf = file_name

    @api.multi
    def generate_cron_for_export(self):
        return {
            'name': _("Generate cron for export"),
            'view_mode': 'form',
            'res_model': 'wizard.myfab.file.interface.cron.mf',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'object_model_name_mf': "myfab.file.interface.export.mf",
                'object_name_mf': self.name,
                'object_id_mf': self.id,
                'object_method_mf': "export_work_orders"
            }
        }

    @api.multi
    def delete_cron_for_export(self):
        self.env["ir.cron"].search([
            ("model", "=", "myfab.file.interface.export.mf"),
            ("function", "=", "export_work_orders"),
            ("args", "=", repr([self.id]))
        ], None, 1).unlink()

    @api.multi
    def download_last_export(self):
        return self.env['binary.download'].execute(
            base64.b64encode(self.last_json_generated_mf),
            self.last_json_generated_name_mf
        )

    @api.multi
    def download_current_export_default_import(self):
        work_orders = self.get_work_orders_to_send_to_myfab_file_interface()
        json_content = []
        for work_order in work_orders:
            if work_order.state == "plan" or work_order.state == "ready" or work_order.state == "progress":
                json_content.extend(work_order.get_resources_default_import_array())
        now = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y%m%d_%H%M%S")
        return self.env['binary.download'].execute(
            base64.b64encode(json.dumps(json_content, indent=4)),
            "Import-WorkOrders-" + now + ".json"
        )
