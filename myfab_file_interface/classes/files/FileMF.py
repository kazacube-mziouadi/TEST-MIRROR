from openerp import models, fields, api, registry, _
import base64
from openerp.addons.web.controllers.main import binary_content


class FileMF(models.Model):
    _name = "file.mf"
    _description = "MyFab file"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", help='')
    content_mf = fields.Binary(string="Content")
    content_preview_mf = fields.Text(string="Content preview", compute="_compute_content_preview")

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.one
    def _compute_content_preview(self):
        # Only way to get the file content string from a binary file field : call the above specific Odoo route...
        # TODO : regarder comment les previews sont realisees dans OpenProd
        status_code, headers, content_base64 = binary_content(model=self._name, id=self.id, field="content_mf")
        self.content_preview_mf = base64.b64decode(content_base64)

    @api.multi
    def download_file(self):
        return self.env["binary.download"].execute(
            self.content_mf,
            self.name
        )
