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
    mf_fields_ids = fields.One2many("mf.simulation.config.field", "mf_simulation_config_id", string="Configurable fields")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.model
    def create(self, fields_list):
        # We write the simulation's name using it's sequence
        fields_list["mf_fields_ids"] = self.get_mf_fields_ids()
        res = super(MFSimulationConfig, self).create(fields_list)
        self._set_fields_order(res.mf_fields_ids)
        return res

    @api.one
    def mf_update(self):
        field_names_present_in_list = []
        for config_field in self.mf_fields_ids:
            field_names_present_in_list.append(config_field.mf_field_id.name)

        global_field_list = self._mf_get_field_list()
        if len(field_names_present_in_list) != len(global_field_list):
            simulation_config_fields_update_list =[]
            for field_id in global_field_list:
                if field_id.name not in field_names_present_in_list:
                    simulation_config_fields_update_list.append((0, 0, {"mf_field_id": field_id.id}))
            vals = {
                'mf_fields_ids': simulation_config_fields_update_list,
            }
            self.write(vals)
        self._set_fields_order(self.mf_fields_ids)

    def _set_fields_order(self, field_list_ids):
        order = 0
        for field_name in self.get_configurable_simulation_fields_names_list():
            for field_config_id in field_list_ids:
                if field_config_id.mf_field_id.name == field_name and field_config_id.sequence != order:
                    field_config_id.sequence = order
            order += 1

    def get_mf_fields_ids(self):
        simulation_config_fields_create_list = []
        for field_id in self._mf_get_field_list():
            simulation_config_fields_create_list.append((0, 0, {"mf_field_id": field_id.id}))
        return simulation_config_fields_create_list

    def _mf_get_field_list(self):
        model_id = self.env["ir.model"].search([("model", '=', "mf.simulation.by.quantity.line")], None, 1)
        configurable_simulation_fields_ids = self.env["ir.model.fields"].search([
            ("name", "in", self.get_configurable_simulation_fields_names_list()),
            ("model_id", '=', model_id.id)
        ])
        return configurable_simulation_fields_ids

    def get_configurable_simulation_fields_names_list(self):
        return self.env["mf.simulation.by.quantity.line"].get_configurable_simulation_fields_names_list()

