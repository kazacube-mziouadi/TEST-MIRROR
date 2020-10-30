from openerp import models, fields, api, _

class ScoreHistoryMF(models.Model):
    _name="score.history.mf"
    _description="history of partner scores"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    score_mf = fields.Integer(string="Score", required=True)
    date_mf = fields.Date(string="Date", required=True)
    partner_id_mf = fields.Many2one("res.partner", string="Partner", ondelete="cascade")