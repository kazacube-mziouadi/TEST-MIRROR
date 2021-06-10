from openerp import models, fields, api, _
import datetime


class MrpWorkorder(models.Model):
    # Inherits MRP WorkOrder
    _inherit = "mrp.workorder"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def get_resources_array(self):
        resources_names_array = {}
        for resource in self.wo_resource_ids:
            resources_names_array[resource.display_name] = {
                "resource_id": {
                    "name": resource.resource_id.name,
                    "type": resource.resource_id.type,
                    "area_id": {
                        "name": resource.resource_id.area_id.name
                    }
                }
            }
        return resources_names_array

    def get_raw_materials_array(self):
        raw_materials_array = {}
        for raw_material in self.rm_draft_ids:
            raw_materials_array[raw_material.display_name] = {
                "product_id": {
                    "name": raw_material.product_id.name,
                    "code": raw_material.product_id.code
                },
                "uom_qty": raw_material.uom_qty,
                "uom_id": {
                    "name": raw_material.uom_id.name
                },
                "consumption_state": raw_material.state
            }
        return raw_materials_array

    def get_final_products_array(self):
        final_products_array = {}
        for final_product in self.fp_draft_ids:
            final_products_array[final_product.display_name] = ({
                "product_id": {
                    "name": final_product.product_id.name,
                    "code": final_product.product_id.code,
                    "track_label": final_product.product_id.track_label
                },
                "uom_id": {
                    "name": final_product.uom_id.name
                },
                "uom_qty": final_product.uom_qty
            })
        return final_products_array

    def get_resources_default_import_array(self):
        now = datetime.datetime.now() + datetime.timedelta(hours=2)
        resources_default_import_array = []
        for resource in self.wo_resource_ids:
            resources_default_import_array.append({
                "model": "wizard.create.timetracking",
                "method": "create",
                "callback": "create_timetracking",
                "fields": {
                    "activity_id": {
                        "name": "Production"
                    },
                    "duration": resource.total_time_theo,
                    "start_date": self.planned_start_date,
                    "end_date": self.planned_end_date,
                    "name": "Timetracking-" + self.display_name + '-' + now.strftime("%Y%m%d_%H%M%S"),
                    "resource_id": {
                        "name": resource.resource_id.name
                    },
                    "target_type": "wo",
                    "wo_id": {
                        "mo_id": {
                            "name": self.mo_id.name
                        },
                        "sequence": self.sequence
                    }
                }
            })
            if resource.resource_id.id == self.first_resource_id.id:
                resources_default_import_array.extend([{
                    "model": "wo.declaration.main",
                    "method": "create",
                    "callback": "action_validate",
                    "fields": {
                        "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "is_forcing_declaration_date": True,
                        "product_id": {
                            "code": self.final_product_id.code
                        },
                        "quantity": self.quantity,
                        "type": "cons_prod",
                        "uom_id": {
                            "name": self.uom_id.name
                        },
                        "wo_id": {
                            "mo_id": {
                                "name": self.mo_id.name
                            },
                            "sequence": self.sequence
                        }
                    }
                }, {
                    "model": "wo.declaration.consumption",
                    "method": "search",
                    "callback": "action_validate",
                    "fields": {
                        "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "wo_id": {
                            "mo_id": {
                                "name": self.mo_id.name
                            },
                            "sequence": self.sequence
                        }
                    }
                }])
                for product_of_work_order in self.fp_draft_ids:
                    if product_of_work_order.product_id.track_label:
                        resources_default_import_array.append({
                            "model": "wo.declaration.produce",
                            "method": "write",
                            "callback": "generate_label",
                            "fields": {
                                "consumption_id": {
                                    "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                                    "wo_id": {
                                        "mo_id": {
                                            "name": self.mo_id.name
                                        },
                                        "sequence": self.sequence
                                    }
                                }
                            },
                            "write": {
                                "nb_label": 1,
                                "qty_label": self.uom_qty
                            }
                        })
                    resources_default_import_array.append({
                        "model": "wo.declaration.produce",
                        "method": "search",
                        "callback": "action_validate",
                        "fields": {
                            "consumption_id": {
                                "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                                "wo_id": {
                                    "mo_id": {
                                        "name": self.mo_id.name
                                    },
                                    "sequence": self.sequence
                                }
                            }
                        }
                    })
        return resources_default_import_array
