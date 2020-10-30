from openerp import models, fields, api, _

class ScoreMF(models.Model):
    _name="score.mf"
    _description="history of partner's scores"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    score_cent_mf = fields.Integer(string="ScoreCent", required=True)
    date_mf = fields.Date(string="Date", required=True)
    partner_id_mf = fields.Many2one("res.partner", string="Partner", ondelete="cascade")