from openerp import models, fields, api, _


class MrpWorkorder(models.Model):
    # Inherits MRP WorkOrder
    _inherit = "mrp.workorder"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def get_resources_names_and_areas_array(self):
        resources_names_array = []
        for resource in self.wo_resource_ids:
            resources_names_array.append({
                "name": resource.resource_id.name,
                "type": resource.resource_id.type,
                "area": resource.resource_id.area_id.name
            })
        return resources_names_array
