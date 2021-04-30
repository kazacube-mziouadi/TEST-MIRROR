from openerp import models, fields, api, _


class MrpWorkorder(models.Model):
    # Inherits MRP WorkOrder
    _inherit = "mrp.workorder"

    # ===========================================================================
    # METHODS
    # ===========================================================================

    def get_resources_names_array(self):
        resources_names_array = []
        for resource in self.wo_resource_ids:
            resources_names_array.append(resource.resource_id.name)
        return resources_names_array

    def get_resources_area_names_array(self):
        resources_areas_names_array = []
        for resource in self.wo_resource_ids:
            if resource.resource_id.area_id:
                resources_areas_names_array.append(resource.resource_id.area_id.name)
        return resources_areas_names_array
