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
    is_successful_mf = fields.Boolean(string="Is successful", required=True, readonly=True)
    message_mf = fields.Text(string="Message")
    start_datetime_mf = fields.Datetime(string="Start datetime", required=True, readonly=True)
    end_datetime_mf = fields.Datetime(string="End datetime", readonly=True)
    file_name_mf = fields.Char(string="Processed file name", required=True, readonly=True)
    file_content_mf = fields.Text(string="Processed file content", default="The file content could not be set.", readonly=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.multi
    def download_processed_file(self):
        return self.env["binary.download"].execute(
            base64.b64encode(self.file_content_mf),
            self.file_name_mf
        )
