from openerp import models, fields, api, registry, _
from openerp.exceptions import ValidationError


class MFSignatureConfig(models.Model):
    _name = "mf.signature.config"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_target_model_id = fields.Many2one("ir.model", string="Target model", required=True)
    mf_target_view_id = fields.Many2one("ir.ui.view", string="Target view", required=True)
    mf_signature_fields_ids = fields.Many2many("ir.model.fields", "mf_signature_config_ir_model_fields_rel",
                                               "mf_signature_config_id", "model_field_id", string="Signature fields",
                                               readonly=True)
    mf_signature_view_id = fields.Many2one("ir.ui.view", string="Signature view", readonly=True)
    mf_signature_base_action_rules_ids = fields.Many2many("base.action.rule",
                                                          "mf_signature_base_action_rules_ids_manual_onchange_rel",
                                                          "mf_signature_config_id", "manual_onchange_id", readonly=True,
                                                          string="Signature base action rules")
    mf_target_model_name = fields.Char(string="Model name", compute="_compute_mf_target_model_name")

    # ===========================================================================
    # METHODS - MODEL
    # ===========================================================================
    @api.one
    @api.depends("mf_target_model_id")
    def _compute_mf_target_model_name(self):
        self.mf_target_model_name = self.mf_target_model_id.model

    @api.onchange("mf_target_model_id")
    def _onchange_mf_target_model_id(self):
        self.mf_target_view_id = False

    @api.model
    def create(self, fields_list):
        if self.env["ir.model.fields"].search([
            ("name", "in", ["x_mf_signature", "x_mf_signature_contact_id", "x_mf_signature_date"]),
            ("model_id", "=", fields_list["mf_target_model_id"])
        ]):
            raise ValidationError(_("There is already a signature field in the chosen model."))
        signature_config_id = super(MFSignatureConfig, self).create(fields_list)
        signature_config_id.mf_signature_fields_ids = [(6, 0, signature_config_id.create_fields())]
        self.env.cr.commit()
        signature_config_id.mf_signature_view_id = signature_config_id.create_fields_view()
        signature_config_id.mf_signature_base_action_rules_ids = [(6, 0, signature_config_id.create_base_action_rule())]
        return signature_config_id

    @api.one
    def unlink(self):
        self.mf_signature_view_id.unlink()
        for base_action_rule_id in self.mf_signature_base_action_rules_ids:
            base_action_rule_id.server_action_ids.unlink()
            base_action_rule_id.unlink()
        self.mf_signature_fields_ids.unlink()
        super(MFSignatureConfig, self).unlink()

    # ===========================================================================
    # METHODS - SIGNATURE GENERATION
    # ===========================================================================

    def create_fields(self):
        # Can not use (0, 0, dict) syntax here (triggers an error)
        fields_ids = [
            self.env["ir.model.fields"].create({
                "name": "x_mf_signature",
                "model_id": self.mf_target_model_id.id,
                "field_description": _("Signature"),
                "ttype": "binary",
                "bin_filename": "x_mf_signature_filename",
            }),
            self.env["ir.model.fields"].create({
                "name": "x_mf_signature_contact_id",
                "model_id": self.mf_target_model_id.id,
                "field_description": _("Signing contact"),
                "ttype": "many2one",
                "relation": "res.partner",
            }),
            self.env["ir.model.fields"].create({
                "name": "x_mf_signature_datetime",
                "model_id": self.mf_target_model_id.id,
                "field_description": _("Signature datetime"),
                "ttype": "datetime",
                "readonly": True,
                "compute": """
for record in self:
    if record.x_mf_signature and record.x_mf_signature_contact_id:
        record['x_mf_signature_datetime'] = datetime.datetime.now()
                """,
                "depends": "x_mf_signature",
                "is_stored_compute": True
            }),
            self.env["ir.model.fields"].search([
                ("name", '=', "x_mf_signature_filename"), ("model_id", '=', self.mf_target_model_id.id)
            ]),
        ]
        return map(lambda field_id: field_id.id, fields_ids)

    def create_fields_view(self):
        view_id = self.env["ir.ui.view"].create({
            "name": "x_mf_signature_" + self.mf_target_model_id.model.replace('.', '_'),
            "type": "form",
            "model": self.mf_target_model_id.model,
            "inherit_id": self.mf_target_view_id.id,
            "mode": "extension",
            "arch_base": """
                <xpath expr="//notebook" position="inside">
                    <page string="
                    """ + _("Electronic signature") + """
                    ">
                        <group col="1" string="
                        """ + _("Electronic signature") + """
                        ">
                            <group col="4">
                                <field name="x_mf_signature_contact_id"  
                                       attrs="{'readonly': [('x_mf_signature', '!=', False), ('x_mf_signature_datetime', '!=', False)]}"/>
                                <field name="x_mf_signature_datetime"/>
                            </group>
                            <group col="2">
                                <label for="x_mf_signature" string="
                                    """ + _("Contact signature") + """
                                "/>
                                <h2>
                                    <field name="x_mf_signature" widget="signature"/>
                                </h2>
                            </group>
                        </group>
                    </page>
                </xpath>
            """,
        })
        return view_id.id

    def create_base_action_rule(self):
        base_action_rules_ids = [self.env["base.action.rule"].create({
            "name": _("Signature contact base action rule for model ") + self.mf_target_model_id.model,
            "model_id": self.mf_target_model_id.id,
            "active": True,
            "kind": "on_create_or_write",
            "server_action_ids": [(0, 0, {
                "name": _("Signature contact action server for model ") + self.mf_target_model_id.model,
                "model_id": self.mf_target_model_id.id,
                "state": "code",
                "code": """
if object.x_mf_signature and not object.x_mf_signature_contact_id:
    raise Warning('""" + _("Please specify the signing contact.") + """')
                """
            })]
        })]
        return map(lambda base_action_rule_id: base_action_rule_id.id, base_action_rules_ids)
