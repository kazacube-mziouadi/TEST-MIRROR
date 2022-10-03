from openerp import models, fields, api, _, modules

class MFSimulationConfig(models.Model):
    _name = "mf.simulation.config"
    _description = "myfab Simulation by quantity"
    _sql_constraints = [
        (
            "name",
            "UNIQUE(name)",
            "There can only be one simulation by quantity config"
        )
    ]

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", default=_("Simulation global configuration"), readonly=True)
    mf_fields_ids = fields.One2many("mf.simulation.config.field", "mf_simulation_config_id",
                                    string="Configurable fields")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.model
    def create(self, fields_list):
        # We write the simulation's name using it's sequence
        fields_list["mf_fields_ids"] = self.get_mf_fields_ids()
        return super(MFSimulationConfig, self).create(fields_list)

    def get_mf_fields_ids(self):
        simulation_config_fields_create_list = []
        for field_id in self._mf_get_field_list():
            simulation_config_fields_create_list.append((0, 0, {"mf_field_id": field_id.id}))
        return simulation_config_fields_create_list

    def _mf_get_field_list(self):
        configurable_simulation_fields_ids = self.env["ir.model.fields"].search([
            ("name", "in", self.get_configurable_simulation_fields_names_list())
        ])
        return configurable_simulation_fields_ids

    def get_configurable_simulation_fields_names_list(self):
        return self.env["mf.simulation.by.quantity.line"].get_configurable_simulation_fields_names_list()

