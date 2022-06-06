from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class mf_create_signature(models.TransientModel):
    _name = "mf.create.signature"

    mf_model_id = fields.Many2one('ir.model', string='Model', required=True)
    mf_view_id = fields.Many2one('ir.ui.view', string='View', required=True, domain=[('type', '=', 'form')])

    @api.multi
    def validate(self):
        field_model = self.env['ir.model.fields']
        view_model = self.env['ir.ui.view']
        alread_exist = field_model.search([('name','=','x_mf_signature'),('model_id','=',self.mf_model_id.id)])
        field_model.create({
            "name":"x_mf_signature",
            "model_id":self.mf_model_id.id,
            "field_description":"Signature",
            "ttype":"binary",
            "bin_filename":"x_mf_signature_filename"
        })
        self.env.cr.commit()
        view_model.create({
            "name":"x_mf_signature_" + self.mf_model_id.model,
            "type":"form",
            "model":self.mf_model_id.model,
            "inherit_id":self.mf_view_id.id,
            "mode":"extension",
            "arch_base":
            """
            <xpath expr="//notebook" position="inside">
                <page string="Electronic signature">
                    <group colspan="8" col="8" string="Electronic signature">
                        <label for="x_mf_signature" string="Client signature" />
                        <h2>
                            <field name="x_mf_signature" widget="signature"/>
                        </h2>
                    </group>
                </page>
            </xpath>
            """,
        })
        
