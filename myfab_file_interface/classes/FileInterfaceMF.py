from openerp import models, fields, api, registry, _
from datetime import datetime


class FileInterfaceMF(models.AbstractModel):
    _name = "file.interface.mf"
    _description = "MyFab file interface configuration"
    _auto = False
    # TODO : creer un dossier a la duplication avec le nom + (1) par exemple = copy ORM
    _sql_constraints = [
        (
            "directory_unique_mf",
            "UNIQUE(directory_mf)",
            "There can only be one file interface attached to a directory"
        )
    ]

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=128, required=True)
    directory_mf = fields.Many2one("physical.directory.mf", string="Directory to process", ondelete="cascade",
                                   help="The directory where are stored the files processed by the file interface.",
                                   required=True)
    directory_path_mf = fields.Char(related="directory_mf.path_mf", string="Directory's path", readonly=True)
    directory_files_mf = fields.One2many(related="directory_mf.files_mf", string="Directory's files", readonly=True)
    directory_scan_is_needed_mf = fields.Boolean(related="directory_mf.directory_scan_is_needed_mf", readonly=True)
    cron_already_exists_mf = fields.Boolean(compute="_compute_cron_already_exists", readonly=True)
    file_extension_mf = fields.Selection(
        [("json", "JSON"), ("csv", "CSV"), ("txt", "TXT")], "File extension", default="json", required=True
    )
    file_separator_mf = fields.Char(string="File data separator", default=",")
    file_quoting_mf = fields.Char(string="File data quoting", default='"')

    # ===========================================================================
    # METHODS - COMPUTE
    # ===========================================================================

    @api.one
    def _compute_cron_already_exists(self):
        existing_cron_for_self = self.env["ir.cron"].search([
            ("model", "=", self._name),
            ("args", "=", repr([self.id]))
        ], None, 1)
        self.cron_already_exists_mf = True if existing_cron_for_self else False

    # ===========================================================================
    # METHODS - STATIC
    # ===========================================================================

    @staticmethod
    def get_current_datetime():
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

    # ===========================================================================
    # METHODS - BUTTONS
    # ===========================================================================

    @api.multi
    def launch_button(self):
        self.launch()

    @api.multi
    def generate_cron(self):
        return {
            "name": _("Generate cron for file interface"),
            "view_mode": "form",
            "res_model": "wizard.file.interface.cron.mf",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {
                "record_model_name_mf": self._name,
                "record_name_mf": self.name,
                "record_id_mf": self.id,
                "record_method_mf": "launch"
            }
        }

    @api.multi
    def delete_cron(self):
        self.env["ir.cron"].search([
            ("model", "=", self._name),
            ("function", "=", "launch"),
            ("args", "=", repr([self.id]))
        ], None, 1).unlink()

    @api.multi
    def scan_directory(self):
        self.directory_mf.scan_directory()
