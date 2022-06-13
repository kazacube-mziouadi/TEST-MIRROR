from openerp import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class mf_create_signature(models.TransientModel):
    _name = "mf.create.signature"

    mf_model_id = fields.Many2one("ir.model", string="Model", required=True)
    mf_view_id = fields.Many2one("ir.ui.view", string="View", required=True, domain=[("type", "=", "form")])

    @api.multi
    def validate(self):
        if self.env["ir.model.fields"].search([
            ("name", "in", ["x_mf_signature", "x_mf_signature_contact_id", "x_mf_signature_date"]),
            ("model_id", "=", self.mf_model_id.id)
        ]):
            raise ValueError(_("There is already a signature field in the model " + self.mf_model_id.model + "."))
        self.create_fields()
        self.env.cr.commit()
        self.create_fields_view()
        self.create_manual_onchange()

    def create_fields(self):
        self.mf_model_id.field_id = [
            (0, 0, {
                "name": "x_mf_signature",
                "field_description": "Signature",
                "ttype": "binary",
                "bin_filename": "x_mf_signature_filename",
            }),
            (0, 0, {
                "name": "x_mf_signature_contact_id",
                "field_description": "Signing contact",
                "ttype": "many2one",
                "relation": "res.partner",
            }),
            (0, 0, {
                "name": "x_mf_signature_datetime",
                "field_description": "Signature datetime",
                "ttype": "datetime",
            }),
        ]

    def create_fields_view(self):
        self.env["ir.ui.view"].create({
            "name": "x_mf_signature_" + self.mf_model_id.model,
            "type": "form",
            "model": self.mf_model_id.model,
            "inherit_id": self.mf_view_id.id,
            "mode": "extension",
            "arch_base": """
                <xpath expr="//notebook" position="inside">
                    <page string="Electronic signature">
                        <group colspan="8" col="8" string="Electronic signature">
                            <group col="4">
                                <field name="x_mf_signature_contact_id"/>
                                <field name="x_mf_signature_date"/>
                            </group>
                            <label for="x_mf_signature" string="Client signature" />
                            <h2>
                                <field name="x_mf_signature" widget="signature"/>
                            </h2>
                        </group>
                    </page>
                </xpath>
            """,
        })

    def create_manual_onchange(self):
        x_mf_signature_datetime_field_id = self.env["ir.model.fields"].search([
            ("name", "=", "x_mf_signature_datetime"),
            ("model_id", "=", self.mf_model_id.id)
        ])
        self.env["manual.onchange"].create({
            "name": _("Signature datetime OnChange for model ") + self.mf_model_id.model,
            "model_id": self.mf_model_id.id,
            "field_ids": [(4, x_mf_signature_datetime_field_id.id)],
            "code": """
                if object.x_mf_signature:
                    res['x_mf_signature_datetime'] = datetime.datetime.now()
            """,
        })
