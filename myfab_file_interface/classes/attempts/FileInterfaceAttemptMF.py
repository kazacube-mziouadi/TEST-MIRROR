from openerp import models, fields, api, registry, _
import base64


class FileInterfaceAttemptMF(models.AbstractModel):
    _name = "file.interface.attempt.mf"
    _description = "MyFab file interface attempt"
    _auto = False

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, help='')
    is_successful_mf = fields.Boolean(string="Is successful", readonly=True)
    message_mf = fields.Text(string="Message")
    start_datetime_mf = fields.Datetime(string="Start datetime", required=True, readonly=True)
    end_datetime_mf = fields.Datetime(string="End datetime", readonly=True)
    file_name_mf = fields.Char(string="Processed file name", required=True, readonly=True)
    file_content_mf = fields.Binary(string="Processed file content binary", required=True)
    file_content_preview_mf = fields.Text(string="Processed file content", compute="_compute_file_content_preview")
    status_mf = fields.Text(compute="_compute_status", string="Status", readonly=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.one
    def _compute_file_content_preview(self):
        self.file_content_preview_mf = str(base64.b64decode(self.file_content_mf))

    @api.one
    def _compute_status(self):
        self.status_mf = "Success" if self.is_successful_mf else "Failed"

    @api.multi
    def download_processed_file(self):
        return self.env["binary.download"].execute(
            self.file_content_mf,
            self.file_name_mf
        )
