from openerp import models, fields, api, _, modules
from openerp.exceptions import ValidationError
import datetime
import logging

_logger = logging.getLogger(__name__)
class mrp_manufacturingorder(models.Model):
    """
        Workorder
    """
    _inherit = 'mrp.manufacturingorder'
    mf_is_d_d15 = fields.Boolean(string='Is today to today +15', compute='_compute_planned_date', search='_search_mf_is_d_d15')
    mf_is_wm1_wp1 = fields.Boolean(string='Is current week -1 to current week +1', compute='_compute_planned_date', search='_search_mf_is_wm1_wp1')
    mf_planned_start_date = fields.Char(string='Planned Start Date Mf', compute='_compute_planned_date', store=True)
    mf_planned_start_week = fields.Char(string='Planned Start Week', compute='_compute_planned_date', store=True)
    mf_planned_ressource_id = fields.Many2one("mf.planned.ressource", string="Planned Ressource")
    mf_planned_ressource_color = fields.Char(string="Planned Ressource color", related="mf_planned_ressource_id.mf_color")
    mf_planned_ressource_name = fields.Char(string="Planned Ressource name", related="mf_planned_ressource_id.name", store=True)
    mf_planned_ressource_config = fields.Boolean(string="Activate Planned ressource management", compute='test')

    @api.one
    def test(self):
        self.mf_planned_ressource_config = self.env['mf.production.config'].search([]).mf_planned_ressource
    
    @api.one
    @api.depends('workorder_ids', 'workorder_ids.planned_start_date', 'workorder_ids.planned_end_date')
    def _compute_planned_date(self):
        _logger.info(self.planned_end_date)
        first_workorder_rcs = self.env['mrp.workorder']
        for wo in self.workorder_ids:
            if not wo.prev_wo_ids:
                first_workorder_rcs += wo
        if first_workorder_rcs:
            first_date = [x.planned_start_date for x in first_workorder_rcs if x.planned_start_date]
            planned_start_date = first_date and min(first_date) or False
        if planned_start_date:
            date = datetime.datetime.strptime((planned_start_date[0:10]), '%Y-%m-%d').date()
            self.mf_is_d_d15 = date>=datetime.date.today() and date<= datetime.date.today() + datetime.timedelta(days=15)
            self.mf_is_wm1_wp1 = date>= datetime.date.today() - datetime.timedelta(weeks=1) and date<= datetime.date.today() + datetime.timedelta(weeks=1)
            self.mf_planned_start_date = (str(date.day) if date.day>10 else "0"+str(date.day))+"/"+(str(date.month) if date.month>10 else "0"+str(date.month))+"/"+str(date.year)
            self.mf_planned_start_week = "S" + str(date.isocalendar()[1])+"/"+str(date.year)
        return super(mrp_manufacturingorder, self)._compute_planned_date()

    def _search_mf_is_d_d15(self, operator, value):
        """
            Fonction search qui permet de retrouver tous les OF qui ont une Date de debut planifiee entre aujourd'hui et +15 jours
        """
        request = """
        SELECT
            x.mo_id
        FROM
			(select min(wo.planned_start_date) as planned_start_date,mo_id as mo_id from mrp_workorder wo group by mo_id) x
        WHERE
            x.planned_start_date >= current_date
            and x.planned_start_date <= current_date + interval '15 day'
        """
        self.env.cr.execute(request)
        res_ids = self.env.cr.fetchall()
        return [('id', 'in', res_ids)]

    def _search_mf_is_wm1_wp1(self, operator, value):
        """
            Fonction search qui permet de retrouver tous les OF qui ont Date de debut planifiee entre la semaine derniere et la semaine prochaine
        """
        request = """
        SELECT
            x.mo_id
        FROM
			(select min(wo.planned_start_date) as planned_start_date,mo_id as mo_id from mrp_workorder wo group by mo_id) x
        WHERE
            x.planned_start_date >= current_date - interval '1 week'
            and x.planned_start_date <= current_date + interval '1 week'
            
        """
        self.env.cr.execute(request)
        res_ids = self.env.cr.fetchall()
        return [('id', 'in', res_ids)]