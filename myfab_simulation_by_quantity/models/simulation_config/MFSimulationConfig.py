from openerp import models, fields, api, _, modules

CONFIGURABLE_SIMULATION_FIELDS_NAMES_LIST = [
    "mf_price_consumable",
    "mf_price_workforce",
    "mf_general_costs",
    "mf_unit_margin",
]


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
        configurable_simulation_fields_ids = self.env["ir.model.fields"].search([
            ("name", "in", CONFIGURABLE_SIMULATION_FIELDS_NAMES_LIST)
        ])
        simulation_config_fields_create_list = []
        for field_id in configurable_simulation_fields_ids:
            simulation_config_fields_create_list.append((0, 0, {"mf_field_id": field_id.id}))
        return simulation_config_fields_create_list

    @staticmethod
    def get_configurable_simulation_fields_names_list():
        return CONFIGURABLE_SIMULATION_FIELDS_NAMES_LIST
