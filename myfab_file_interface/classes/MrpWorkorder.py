from openerp import models, fields, api, _


class MrpWorkorder(models.Model):
    # Inherits MRP WorkOrder
    _inherit = "mrp.workorder"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def get_resources_array(self):
        resources_names_array = []
        for resource in self.wo_resource_ids:
            resources_names_array.append({
                "resource_id": {
                    "name": resource.resource_id.name,
                    "type": resource.resource_id.type,
                    "area_id": {
                        "name": resource.resource_id.area_id.name
                    }
                }
            })
        return resources_names_array

    def get_raw_materials_array(self):
        raw_materials_array = []
        for raw_material in self.rm_draft_ids:
            raw_materials_array.append({
                "product_id": {
                    "name": raw_material.product_id.name,
                    "code": raw_material.product_id.code
                },
                "uom_qty": raw_material.uom_qty,
                "uom_id": {
                    "name": raw_material.uom_id.name
                },
                "consumption_state": raw_material.state
            })
        return raw_materials_array
