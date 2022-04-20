from openerp import models, fields, api, registry, _


class FileInterfaceAttemptMF(models.AbstractModel):
    _name = "file.interface.attempt.mf"
    _description = "myfab file interface attempt"
    _auto = False

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(string="Name", size=64, help='')
    message_mf = fields.Text(string="Message")
    start_datetime_mf = fields.Datetime(string="Start datetime", required=True, readonly=True)
    end_datetime_mf = fields.Datetime(string="End datetime", readonly=True)
    file_mf = fields.Many2one("file.mf", string="Processed file", required=False, ondelete="cascade")
    file_name_mf = fields.Char(related="file_mf.name", string="File name", readonly=True)
    is_successful_mf = fields.Boolean(string="Is successful", readonly=True)
    status_mf = fields.Char(compute="_compute_status", string="Status", readonly=True)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.one
    def _compute_status(self):
        self.status_mf = "Success" if self.is_successful_mf else "Failed"
