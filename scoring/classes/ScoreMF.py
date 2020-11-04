from openerp import models, fields, api, _

class ScoreMF(models.Model):
    _name="score.mf"
    _description="history of partner's scores"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    score_hundred_mf = fields.Integer(string="Score Hundred", required=True)
    score_twenty_mf = fields.Integer(string="Score Twenty", required=True)
    date_mf = fields.Date(string="Date", required=True)
    partner_id_mf = fields.Many2one("res.partner", string="Partner", ondelete="cascade")

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @staticmethod
    def create_from_object_temp(score_api, partner):
        return {
            "score_hundred_mf": score_api.find("{http://risque.vo.callisto.newsys.altares.fr/xsd}scoreCent").text,
            "score_twenty_mf": score_api.find("{http://risque.vo.callisto.newsys.altares.fr/xsd}scoreVingt").text,
            "date_mf": score_api.find("{http://risque.vo.callisto.newsys.altares.fr/xsd}dateValeur").text,
            "partner_id_mf": partner.id
        }

    @api.one
    @api.depends("score_hundred_mf")
    def _compute_score_hundred_to_twenty(self):
        self.score_twenty_mf = round(self.score_hundred_mf / 5, 0)
