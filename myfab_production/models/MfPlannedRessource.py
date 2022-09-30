from openerp import models, fields, api, _, modules
from openerp.exceptions import ValidationError
from openerp.osv import expression
import logging

_logger = logging.getLogger(__name__)

class MFPlannedRessource(models.Model):
    _name = "mf.planned.ressource"

    name = fields.Char(string="Name")
    mf_description = fields.Char(string="Description")
    mf_color = fields.Char(string="Color", default='#FFFFFF')
    mf_number_ressources = fields.Integer(string="Number of ressources")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=1000):
        """
            Fonction name_search de la nomenclature
        """
        domain = [expression.get_logical_operator(operator), ('mf_description', operator, name), ('name', operator, name)]
        return super(MFPlannedRessource, self).name_search(name=name, args=expression.AND([domain, args]), operator=operator, limit=limit)
