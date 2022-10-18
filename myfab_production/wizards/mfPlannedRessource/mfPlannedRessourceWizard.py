# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class mf_planned_ressource_wizard(models.TransientModel):
    """ 
        Wizard to change planned ressource
    """
    _name = 'planned.ressource.wizard'

    mf_mo_id = fields.Many2one("mrp.manufacturingorder", string="Manufactoring order")
    mf_planned_ressource_id = fields.Many2one("mf.planned.ressource", string="Planned Ressource")

    @api.model
    def default_get(self, fields_list):
        """
            Récupération des informations de la ligne
        """
        res = super(mf_planned_ressource_wizard, self).default_get(fields_list=fields_list)
        context = self.env.context
        if context.get('active_model') == 'mrp.manufacturingorder':
            mo_rc = self.env['mrp.manufacturingorder'].browse(self.env.context.get('active_id'))
            res['mf_mo_id'] = mo_rc.id
        return res

    @api.multi
    def change_ressource(self):
        self.mf_mo_id.mf_planned_ressource_id = self.mf_planned_ressource_id.id
        return {'type': 'ir.actions.act_window_view_reload'}
