from openerp import models, fields, api, registry, _
import base64
from openerp.addons.web.controllers.main import binary_content


class FileMF(models.Model):
    _name = "file.mf"
    _description = "MyFab file"
    _order = "sequence"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", help='')
    content_mf = fields.Binary(string="Content")
    content_preview_mf = fields.Text(string="Content preview", compute="_compute_content_preview")
    sequence = fields.Integer(string="Sequence", compute="_compute_sequence", store=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.model
    def create(self, fields_list):
        fields_list["content_mf"] = base64.b64encode(fields_list["content_mf"])
        return super(FileMF, self).create(fields_list)

    @api.one
    def _compute_content_preview(self):
        # Only way to get the file content string from a binary file field : call the above specific Odoo route...
        status_code, headers, content_base64 = binary_content(model=self._name, id=self.id, field="content_mf")
        self.content_preview_mf = base64.b64decode(content_base64)

    @api.one
    @api.depends('name')
    def _compute_sequence(self):
        sequence = self.get_sequence_from_file_name(self.name)
        if sequence:
            self.sequence = sequence

    @api.multi
    def download_file(self):
        return self.env["binary.download"].execute(
            self.content_mf,
            self.name
        )

    # Returns the model name from a given import file name
    @staticmethod
    def get_model_name_from_file_name(file_name):
        file_name_split_hyphen = file_name.split('-')
        file_name_split_dot = file_name_split_hyphen[-1].split('.')
        file_name_split_dot.pop()
        return '.'.join(file_name_split_dot)

    # Returns the sequence int from a given import file name if it begins with an int ; else, returns False
    @staticmethod
    def get_sequence_from_file_name(file_name):
        if type(file_name) is not str and not isinstance(file_name, unicode):
            file_name = file_name.name
        file_name_split_hyphen = file_name.split('-')
        return int(file_name_split_hyphen[0]) if file_name_split_hyphen[0].isdigit() else False
